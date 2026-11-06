#!/usr/bin/env python3
"""Index original figure assets and table source from a LaTeX project.

Usage: python scripts/extract_figures.py <paper-directory>
Never crops paper.pdf, executes TeX, or modifies source assets. This is a source
locator, not a TeX interpreter; extracted blocks are reading aids, not standalone
compilable documents. Unsupported macros/conditionals need source inspection.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass
import json
from pathlib import Path
import re
from urllib.parse import quote

COMMAND = r'(?<!\\)\\'
FLOAT = re.compile(COMMAND + r'begin\s*\{(figure\*?|table\*?|longtable)\}')
INCLUDE = re.compile(COMMAND + r'(?:input|include)(?![A-Za-z@])\s*(?:\{([^{}]+)\}|([^\s{}%]+))')
MACRO = re.compile(COMMAND + r'(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)\*?\s*(?:\{\s*\\([A-Za-z@]+)\s*\}|\\([A-Za-z@]+))')
EXTENSIONS = ('.pdf', '.png', '.jpg', '.jpeg', '.eps', '.svg', '.webp')


def blank(text):
    return ''.join('\n' if c == '\n' else ' ' for c in text)


def mask(text):
    """Ignore comments and literal conditionals without changing offsets."""
    chars = list(text)
    for match in re.finditer('%', text):
        pos = match.start()
        backslashes = len(text[:pos]) - len(text[:pos].rstrip('\\'))
        if backslashes % 2:
            continue
        end = text.find('\n', pos)
        end = len(text) if end < 0 else end
        chars[pos:end] = ' ' * (end - pos)
    clean = ''.join(chars)
    for match in re.finditer(r'\\begin\{(comment|verbatim\*?|lstlisting|minted)\}.*?\\end\{\1\}', clean, re.S):
        chars[match.start():match.end()] = blank(match.group())
    clean = ''.join(chars)
    stack, active, previous = [], True, 0
    for match in re.finditer(r'\\(iffalse|iftrue|else|fi)\b', clean):
        if not active:
            chars[previous:match.start()] = blank(clean[previous:match.start()])
        token = match.group(1)
        if token in ('iffalse', 'iftrue'):
            stack.append((active, token == 'iftrue'))
            active = active and token == 'iftrue'
        elif token == 'else' and stack:
            parent, branch = stack[-1]
            stack[-1] = (parent, not branch)
            active = parent and not branch
        elif token == 'fi' and stack:
            active = stack.pop()[0]
        previous = match.end()
    if not active:
        chars[previous:] = blank(clean[previous:])
    return ''.join(chars)


def group(text, pos, opening='{', closing='}'):
    """Read a balanced argument, including nested braces in optional arguments."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos == len(text) or text[pos] != opening:
        return None, pos
    start, depth, braces = pos + 1, 1, 0
    pos += 1
    while pos < len(text):
        c = text[pos]
        if c == '\\':
            pos += 2
            continue
        if opening == '[':
            braces += (c == '{') - (c == '}')
        if not braces:
            depth += (c == opening) - (c == closing)
        if depth == 0:
            return text[start:pos], pos + 1
        pos += 1
    return None, start - 1


def arguments(text, name):
    for match in re.finditer(COMMAND + re.escape(name) + r'(?![A-Za-z@])(\*)?', text):
        pos = match.end()
        options, after = group(text, pos, '[', ']')
        if options is not None:
            pos = after
        value, end = group(text, pos)
        if value is not None:
            yield {'start': match.start(), 'end': end, 'value': value,
                   'options': options, 'starred': bool(match.group(1))}


@dataclass
class Span:
    start: int
    end: int
    path: Path
    offset: int


class Sources:
    def __init__(self, root, main):
        self.root, self.main = root.resolve(), main.resolve()
        self.raw, self.warnings = {}, []
        self.text, self.spans = self.expand(self.main, ())
        self.starts = [s.start for s in self.spans]

    def resolve(self, name, owner, directories=(), extensions=()):
        if '\\' in name or '#' in name or Path(name).is_absolute():
            return None, 'unresolved'
        bases = [self.main.parent, owner.parent]
        bases += [self.main.parent / directory for directory in directories]
        for base in dict.fromkeys(bases):
            path = (base / name).resolve()
            choices = [path] if path.suffix else [path, *(Path(str(path) + ext) for ext in extensions)]
            for choice in choices:
                if self.root in choice.parents and choice.is_file():
                    return choice, 'resolved'
        return None, 'missing'

    def expand(self, path, stack):
        if path in stack or len(stack) >= 30:
            self.warnings.append(f'跳过循环/过深的 input：{path.name}')
            return '', []
        raw = path.read_text(encoding='utf-8', errors='replace')
        self.raw[path] = raw
        text = mask(raw)
        output, spans, size = [], [], 0

        def append(part, part_spans):
            nonlocal size
            output.append(part)
            spans.extend(Span(s.start + size, s.end + size, s.path, s.offset) for s in part_spans)
            size += len(part)

        previous = 0
        for match in INCLUDE.finditer(text):
            part = text[previous:match.start()]
            if part:
                append(part, [Span(0, len(part), path, previous)])
            name = (match.group(1) or match.group(2)).strip()
            if not name.endswith('.tex'):
                name += '.tex'
            child = self.resolve(name, path)[0]
            if child:
                expanded, nested = self.expand(child, (*stack, path))
                append(expanded, nested)
            else:
                self.warnings.append(f'未解析 input：{name}（{path.name}）')
                part = match.group()
                append(part, [Span(0, len(part), path, match.start())])
            previous = match.end()
        part = text[previous:]
        if part:
            append(part, [Span(0, len(part), path, previous)])
        return ''.join(output), spans

    def locate(self, pos):
        span = self.spans[bisect_right(self.starts, pos) - 1]
        offset = span.offset + pos - span.start
        return span.path, self.raw[span.path].count('\n', 0, offset) + 1

    def fragments(self, start, end):
        result = []
        for span in self.spans:
            left, right = max(start, span.start), min(end, span.end)
            if left < right:
                a = span.offset + left - span.start
                b = span.offset + right - span.start
                result.append(self.raw[span.path][a:b])
        return ''.join(result)


def write_changed(path, text):
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


def source_index(paper: Path, main_tex: Path | None = None):
    """Write source indexes and excerpts, never raster images."""
    from fetch_paper import find_main_tex
    paper = paper.resolve()
    root = paper / 'source'
    main = main_tex or find_main_tex(root)
    if main is None:
        return {'figures_status': '无可用 LaTeX 源码，未生成图资源索引（不截图）',
                'tables_status': '无可用 LaTeX 源码，表格需阅读原 PDF 核对'}
    doc = Sources(root, main)
    records = {'figure': [], 'table': []}
    graphics_paths = list(arguments(doc.text, 'graphicspath'))
    extensions = list(arguments(doc.text, 'DeclareGraphicsExtensions'))
    definitions = {}
    for match in MACRO.finditer(doc.text):
        path, line = doc.locate(match.start())
        name = match.group(1) or match.group(2)
        definitions.setdefault(name, []).append((match.start(), str(path.relative_to(paper)), line))

    for match in FLOAT.finditer(doc.text):
        env = match.group(1)
        closing = re.search(r'\\end\s*\{' + re.escape(env) + r'\}', doc.text[match.end():])
        if closing is None:
            doc.warnings.append(f'未闭合环境：{env}')
            continue
        end = match.end() + closing.end()
        body = doc.text[match.start():end]
        kind = 'figure' if env.startswith('figure') else 'table'
        labels = [a['value'].strip() for a in arguments(body, 'label')]
        captions = [a['value'].strip() for a in arguments(body, 'caption')]
        path, line = doc.locate(match.start())
        end_path, end_line = doc.locate(end - 1)
        order = len(records[kind]) + 1
        label = labels[-1] if labels else None
        slug = re.sub(r'[^\w.-]+', '-', label or f'{path.stem}-L{line}').strip('-')
        identifier = ('fig-' if kind == 'figure' else 'tab-') + slug
        if any(r['id'] == identifier for r in records[kind]):
            identifier += f'-L{line}-{order}'
        folder = 'figures' if kind == 'figure' else 'tables'
        snippet = f'{folder}/{identifier}.tex'
        dependencies = []
        local_definitions = {m.group(1) or m.group(2) for m in MACRO.finditer(body)}
        referenced = set(re.findall(r'\\([A-Za-z@]+)', body)) - local_definitions
        for name in sorted(referenced & definitions.keys()):
            candidates = [d for d in definitions[name] if d[0] < match.start()]
            if candidates:
                _, source, definition_line = candidates[-1]
                dependencies.append({'command': '\\' + name, 'source': source, 'line': definition_line})
        header = '% Generated reading excerpt; not a standalone compilable document.\n'
        header += f'% Source: {path.relative_to(paper)}:{line}\n'
        for dep in dependencies:
            header += f"% Macro context: {dep['command']} — {dep['source']}:{dep['line']}\n"
        write_changed(paper / snippet, header + doc.fragments(match.start(), end) + '\n')

        assets = []
        for graphic in arguments(body, 'includegraphics'):
            pos = match.start() + graphic['start']
            owner, graphic_line = doc.locate(pos)
            dirs = []
            for declaration in graphics_paths:
                if declaration['start'] <= pos:
                    dirs = re.findall(r'\{([^{}]+)\}', declaration['value'])
            exts = EXTENSIONS
            for declaration in extensions:
                if declaration['start'] <= pos:
                    exts = tuple(s.strip() for s in declaration['value'].split(','))
            asset, status = doc.resolve(graphic['value'].strip(), owner, dirs, exts)
            assets.append({'reference': graphic['value'], 'options': graphic['options'],
                           'path': str(asset.relative_to(paper)) if asset else None,
                           'status': status, 'source': str(owner.relative_to(paper)), 'line': graphic_line})
        records[kind].append({'id': identifier, 'source_order': order, 'label': label,
                              'captions_tex': captions, 'source': str(path.relative_to(paper)),
                              'line_start': line, 'end_source': str(end_path.relative_to(paper)),
                              'line_end': end_line, 'excerpt': snippet,
                              'macro_context': dependencies, 'assets': assets,
                              'verification': 'source_located_not_visually_verified'})

    unknown_ifs = sorted(set(re.findall(r'\\(if[A-Za-z@]+)\b', doc.text)) - {'iftrue', 'iffalse'})
    if unknown_ifs:
        doc.warnings.append('未求值的条件命令（需核对有效分支）：' + ', '.join(unknown_ifs))
    statuses = {}
    for kind, items in records.items():
        folder = 'figures' if kind == 'figure' else 'tables'
        title = '原始图资源索引' if kind == 'figure' else 'LaTeX 表格源码索引'
        lines = [f'# {title}', '',
                 '> 自动生成。以下顺序是源码出现顺序，不代替论文图表编号；以 label 和原 PDF 核对正文/附录编号。',
                 '> 图直接使用原始资源；片段保留组合排版、文字、图注和表格结构。此流程不截图、不编译。',
                 '> 片段是阅读辅助；外部宏、包、脚注和排版上下文应回到原始源码核对。定位成功不等于已经核验。', '']
        if not items:
            lines += ['未定位到标准图表环境；检查原始源码中的自定义宏或其他环境，不以截图补齐。', '']
        for record in items:
            lines += [f"## {record['source_order']}. {record['label'] or record['id']}", '']
            for caption in record['captions_tex']:
                lines += ['图注/表注（LaTeX）：' + re.sub(r'\s+', ' ', caption), '']
            source_link = quote('../' + record['source'], safe='/')
            excerpt_link = quote(Path(record['excerpt']).name)
            lines += [f"- 原始源码：[{record['source']}]({source_link})，第 {record['line_start']} 行起。",
                      f'- 完整环境片段：[查看 LaTeX]({excerpt_link})。']
            for dep in record['macro_context']:
                link = quote('../' + dep['source'], safe='/')
                lines.append(f"- 宏上下文：`{dep['command']}` → [{dep['source']}]({link}) 第 {dep['line']} 行。")
            for asset in record['assets']:
                if asset['path']:
                    link = quote('../' + asset['path'], safe='/')
                    lines.append(f"- 原始资源：[{asset['path']}]({link})。")
                else:
                    lines.append(f"- 未解析资源：`{asset['reference']}`（{asset['status']}），需检查原始源码。")
                if asset['options']:
                    lines.append(f"  原引用选项：`{asset['options']}`。")
            if kind == 'figure':
                lines.append('- 说明：原始资源可能只是组合图的一部分；同时阅读环境片段中的子图标记、文字和图注。')
                if not record['assets']:
                    lines.append('- 未定位到独立图片文件；可能由 TikZ/PGF 或宏绘制，保留源码并注明，禁止猜测图片对应关系。')
            lines.append('')
        if doc.warnings:
            lines += ['## 待核对', '', *('- ' + warning for warning in doc.warnings), '']
        write_changed(paper / folder / 'index.md', '\n'.join(lines))
        payload = {'schema_version': 1, 'mode': 'latex_source', 'main_tex': str(doc.main.relative_to(paper)),
                   'warnings': doc.warnings, 'items': items}
        write_changed(paper / folder / 'index.json', json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        missing = sum(asset['status'] != 'resolved' for item in items for asset in item['assets'])
        statuses[folder + '_status'] = f'已索引 {len(items)} 个 LaTeX {"图" if kind == "figure" else "表"}环境；{missing} 个资源引用未解析；不截图'
    return statuses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paper_directory', type=Path, help='包含 source/ 的论文目录')
    args = parser.parse_args()
    if not args.paper_directory.is_dir():
        parser.error('请输入论文目录，图表处理直接使用 source/ 中的 LaTeX 资源')
    result = source_index(args.paper_directory)
    meta_path = args.paper_directory / 'meta.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        meta.update(result)
        meta['visual_material_mode'] = 'latex_source'
        write_changed(meta_path, json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
