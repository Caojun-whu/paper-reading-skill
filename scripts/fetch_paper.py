#!/usr/bin/env python3
"""Prepare a paper for interactive reading: PDF + arXiv LaTeX + figures + official code.

Examples:
  python scripts/fetch_paper.py 2410.24164 --dest "Paper-Name"
  python scripts/fetch_paper.py ~/Downloads/paper.pdf --dest "Paper-Name"
  python scripts/fetch_paper.py "Paper-Name" --code https://github.com/author/official-repo

Always run from the current Codex project directory. A new paper requires --dest,
a single folder name (not a path), chosen from the paper title by the Agent.

Only public content is retrieved. Never installs dependencies or executes cloned code.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

UA = 'paper-reading-skill/3.0 (academic paper reading)'
ARXIV_ID = r'(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?'
CODE_RE = re.compile(r'https?://(?:www\.)?(?:github\.com|gitlab\.com)/[\w.-]+/[\w.-]+', re.I)
LIMIT = 300 * 1024 * 1024


def identify(raw: str):
    path = Path(raw).expanduser()
    if path.is_dir() and (path / 'paper.pdf').exists():
        return 'directory', path.resolve(), path.name, None
    if path.is_file():
        return 'local', path.resolve(), path.stem, None
    url = urllib.parse.urlparse(raw)
    if url.scheme in ('https', 'http'):
        match = re.search(r'arxiv\.org/(?:abs|pdf|html)/(' + ARXIV_ID + r')(?:\.pdf)?', raw, re.I)
        if match:
            arxiv = match.group(1)
            return 'remote', f'https://arxiv.org/pdf/{arxiv}', arxiv.replace('/', '-'), arxiv
        slug = re.sub(r'[^\w.-]+', '-', Path(url.path).stem).strip('-') or 'paper'
        return 'remote', raw, slug[:100], None
    if re.fullmatch(ARXIV_ID, raw, re.I):
        return 'remote', f'https://arxiv.org/pdf/{raw}', raw.replace('/', '-'), raw
    raise ValueError('请输入 arXiv ID/链接、PDF 网址、本地 PDF 或已有论文目录')


def download(url: str, target: Path, limit=LIMIT):
    """Atomic, bounded download; never overwrite an existing resource."""
    if target.is_file() and target.stat().st_size:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + '.part')
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, tmp.open('wb') as out:
            size = 0
            while chunk := resp.read(1 << 20):
                size += len(chunk)
                if size > limit:
                    raise ValueError(f'文件超过 {limit // 1048576} MiB 下载限制')
                out.write(chunk)
        if not size:
            raise ValueError('服务器返回空文件')
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)


def pdf_info(path: Path):
    import fitz
    with fitz.open(path) as doc:
        if not doc.is_pdf or not len(doc):
            raise ValueError('不是有效 PDF')
        title = (doc.metadata or {}).get('title') or ''
        pages = []
        for i, page in enumerate(doc):
            pages.append(page.get_text('text', sort=True))
    return title, pages


def arxiv_from_text(pages):
    text = '\n'.join(pages[:2])
    m = re.search(r'arXiv\s*:\s*(' + ARXIV_ID + r')', text, re.I)
    return m.group(1) if m else None


def secure_unpack(blob: bytes, dest: Path) -> int:
    """Support arXiv tar.gz / single gzip TeX; reject paths and links outside source."""
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    try:
        archive = tarfile.open(fileobj=io.BytesIO(blob), mode='r:*')
    except tarfile.TarError:
        archive = None
    if archive:
        total = 0
        with archive:
            for member in archive:
                if member.isdir():
                    continue
                if not member.isfile():
                    continue  # no symlinks or hard links from external archives
                rel = PurePosixPath(member.name)
                if rel.is_absolute() or '..' in rel.parts or not rel.parts:
                    continue
                if member.size > LIMIT or total + member.size > LIMIT or count >= 2500:
                    raise ValueError('LaTeX 附件超过安全的文件数量/大小限制')
                target = dest.joinpath(*rel.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    continue
                with source, target.open('wb') as out:
                    shutil.copyfileobj(source, out)
                total += member.size
                count += 1
        return count
    if blob.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(blob)) as g:
            data = g.read(LIMIT + 1)
    else:
        data = blob
    if len(data) > LIMIT:
        raise ValueError('单文件 LaTeX 超出限制')
    if b'\\documentclass' in data[:50000] or b'\\begin{document}' in data[:50000]:
        (dest / 'main.tex').write_bytes(data)
        return 1
    raise ValueError('arXiv e-print 不是可识别的 TeX 源码')


def find_main_tex(folder: Path) -> Path | None:
    candidates = list(folder.rglob('*.tex'))
    if not candidates:
        return None
    preferred = {'main.tex': 0, 'paper.tex': 1, 'arxiv.tex': 2, 'manuscript.tex': 3}
    def rank(p):
        try:
            s = p.read_text(encoding='utf-8', errors='replace')[:100000]
        except OSError:
            return (3, 99, str(p))
        doc = ('\\documentclass' in s or '\\begin{document}' in s)
        return (0 if doc else 1, preferred.get(p.name.lower(), 10), str(p))
    return sorted(candidates, key=rank)[0]


def strip_tex_comments(s: str) -> str:
    # Preserve escaped \%; sufficient for reading, original .tex remains authoritative.
    return '\n'.join(re.sub(r'(?<!\\)%[^\n]*$', '', line) for line in s.splitlines())


def flatten_tex(path: Path, source_root: Path, visited=None, depth=0) -> str:
    if visited is None:
        visited = set()
    path = path.resolve()
    if source_root.resolve() not in path.parents or path in visited or depth > 30:
        return f'\n% [skipped repeated/unavailable TeX file: {path.name}]\n'
    visited.add(path)
    raw = strip_tex_comments(path.read_text(encoding='utf-8', errors='replace'))
    pattern = re.compile(r'\\(?:input|include)\s*(?:\{([^}]+)\}|\s+([\w./-]+))')
    def replace(m):
        rel = (m.group(1) or m.group(2)).strip()
        child = path.parent / (rel if rel.endswith('.tex') else rel + '.tex')
        if not child.is_file():
            return m.group(0)
        return f'\n% BEGIN include {rel}\n' + flatten_tex(child, source_root, visited, depth + 1) + f'\n% END include {rel}\n'
    return pattern.sub(replace, raw)


def make_outline(text: str, dest: Path):
    lines = ['# LaTeX 论文结构索引', '', '以下行号对应 `paper.tex`。', '']
    pattern = re.compile(r'\\(section|subsection|subsubsection)\*?\{([^}]+)\}')
    for line_no, line in enumerate(text.splitlines(), 1):
        m = pattern.search(line)
        if m:
            title = re.sub(r'\\\w+', '', m.group(2)).strip()
            lines.append(f'- L{line_no} · {m.group(1)} · {title}')
    (dest / 'outline.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def fetch_latex(arxiv: str | None, dest: Path) -> str:
    if not arxiv:
        return '无 arXiv ID，无法自动定位 LaTeX 源码'
    src = dest / 'source'
    if list(src.rglob('*.tex')) if src.exists() else False:
        status = '已有 source/'
    else:
        blob_path = dest / '.arxiv-source.partblob'
        try:
            download(f'https://arxiv.org/e-print/{arxiv}', blob_path)
            count = secure_unpack(blob_path.read_bytes(), src)
            status = f'已下载 LaTeX 源码（{count} 个文件）'
        except (ValueError, OSError, urllib.error.URLError, tarfile.TarError) as e:
            status = f'获取 LaTeX 失败：{e}'
        finally:
            blob_path.unlink(missing_ok=True)
    main = find_main_tex(src) if src.exists() else None
    if main:
        if not (dest / 'paper.tex').exists():
            flattened = flatten_tex(main, src)
            (dest / 'paper.tex').write_text(flattened, encoding='utf-8')
        make_outline((dest / 'paper.tex').read_text(encoding='utf-8'), dest)
    elif src.exists() and not any(src.iterdir()):
        src.rmdir()
    return status


def code_candidates(pages):
    """Candidate URLs in the paper's opening pages, NOT proof of official ownership."""
    results = []
    for p in pages[:3]:
        for m in CODE_RE.finditer(p):
            url = m.group(0).rstrip('.,;:)]}/')
            if url not in results:
                results.append(url)
    return results


def likely_official_code_link(pages, url: str) -> bool:
    # Links in references/related work may be unrelated; require code-availability context.
    for text in pages[:3]:
        for m in re.finditer(re.escape(url), text):
            vicinity = text[max(0, m.start() - 140):m.end() + 35].lower()
            if re.search(r'(our\s+(?:source\s+)?code|code\s+(?:is\s+)?available|official\s+(?:code|implementation)|implementation\s+(?:is\s+)?available|source\s+code\s*[:(]|code\s*[:：])', vicinity):
                return True
    return False


def clone_code(url: str, dest: Path) -> str:
    parsed = urllib.parse.urlparse(url)
    # GitHub/GitLab only, never execute repository contents.
    if parsed.scheme != 'https' or parsed.hostname not in ('github.com', 'www.github.com', 'gitlab.com', 'www.gitlab.com'):
        raise ValueError('请提供 GitHub/GitLab 官方 https 仓库链接')
    if len([x for x in parsed.path.strip('/').split('/') if x]) < 2:
        raise ValueError('仓库链接缺少 owner/project')
    if dest.exists() and any(dest.iterdir()):
        return '已有 code/，未覆盖'
    if shutil.which('git') is None:
        return '未安装 git，无法克隆代码'
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'clone', '--depth', '1', '--', url, str(dest)],
                          capture_output=True, text=True, timeout=180, check=False)
    if proc.returncode != 0:
        if dest.exists() and not any(dest.iterdir()):
            dest.rmdir()
        return 'clone 失败：' + (proc.stderr or proc.stdout).strip()[-300:]
    return '已浅克隆代码（只读，不执行；仍需核实官方归属与版本）'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('paper', help='arXiv ID/链接、PDF URL、本地 PDF 或论文文件夹')
    p.add_argument('--dest', type=Path, help='新论文的文件夹名称，只允许当前项目下的一层目录')
    p.add_argument('--code', help='已核实的官方 GitHub/GitLab 仓库 URL')
    p.add_argument('--no-tex', action='store_true', help='跳过 LaTeX（默认尝试）')
    p.add_argument('--no-code', action='store_true', help='跳过 code（默认尽可能发现）')
    p.add_argument('--no-figures', action='store_true', help='跳过自动裁图（默认尝试）')
    a = p.parse_args()
    kind, src, slug, arxiv = identify(a.paper)
    if a.dest is None and kind != 'directory':
        p.error('新论文必须提供 --dest <论文名称>，例如 --dest Geo2Vec')
    if a.dest is not None:
        if a.dest.is_absolute() or len(a.dest.parts) != 1 or str(a.dest) in ('.', '..'):
            p.error('--dest 只能是当前项目下的一层文件夹名称，不允许使用路径')
        dest = (Path.cwd() / a.dest).resolve()
    else:
        dest = src
    if a.dest and dest.parent != Path.cwd().resolve():
        p.error('论文文件夹必须直接位于当前 Codex 项目目录下')
    dest.mkdir(parents=True, exist_ok=True)
    pdf = dest / 'paper.pdf'
    if not pdf.is_file():
        if kind == 'local':
            if src != pdf:
                shutil.copy2(src, pdf)
        elif kind == 'remote':
            download(src, pdf)
    if not pdf.is_file() or not pdf.stat().st_size:
        raise RuntimeError('未取得有效 PDF')
    title, pages = pdf_info(pdf)
    meta_path = dest / 'meta.json'
    try:
        previous_meta = json.loads(meta_path.read_text('utf-8')) if meta_path.exists() else {}
    except json.JSONDecodeError:
        previous_meta = {}
    arxiv = arxiv or arxiv_from_text(pages) or previous_meta.get('arxiv_id')
    paper_txt = dest / 'paper.txt'
    if not paper_txt.exists():
        paper_txt.write_text(''.join(f'\n===== PDF page {i + 1} =====\n{text}\n' for i, text in enumerate(pages)), encoding='utf-8')
    tex_status = '已跳过' if a.no_tex else fetch_latex(arxiv, dest)
    figure_status = '已跳过'
    if not a.no_figures:
        try:
            from extract_figures import extract_figures
            figure_status = extract_figures(pdf, dest / 'figures')
        except Exception as e:
            figure_status = f'裁图失败（可手动裁）：{e}'
    candidates = code_candidates(pages)
    code_url = a.code or previous_meta.get('code_url')
    if a.no_code:
        code_status = '已跳过'
    elif (dest / 'code').is_dir() and any((dest / 'code').iterdir()):
        code_status = '已有 code/（未覆盖）'
    elif a.code:
        try:
            code_status = clone_code(code_url, dest / 'code')
        except (ValueError, OSError, subprocess.TimeoutExpired) as e:
            code_status = f'代码获取失败：{e}'
    else:
        code_status = '未下载；需先核实官方仓库，再使用 --code URL 补充'
    meta = previous_meta
    meta.update({
        'source_input': a.paper, 'arxiv_id': arxiv, 'pdf_title': title,
        'pdf_pages': len(pages), 'latex_status': tex_status,
        'figures_status': figure_status, 'code_status': code_status,
        'code_url': code_url, 'code_link_candidates': candidates,
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
    })
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('论文目录：' + str(dest))
    print(f'PDF：{len(pages)} 页；文本：{paper_txt.name}')
    print('LaTeX：' + tex_status)
    print('图表：' + figure_status)
    print('代码：' + code_status)
    if candidates:
        print('论文中发现的候选代码链接（尚未核实官方性）：' + '；'.join(candidates))
    print('下一步：检查 figures/_contact.png，确认裁图无误后再讲解；未找到的代码请另查官方来源。')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, urllib.error.URLError) as exc:
        print(f'错误：{exc}', file=sys.stderr)
        sys.exit(1)
