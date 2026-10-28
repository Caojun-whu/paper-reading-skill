#!/usr/bin/env python3
"""Automatically crop figure/table candidates from PDF caption locations.

Heuristic crops require manual verification: always inspect figures/_contact.png.
When a crop is incomplete, re-crop from paper.pdf with crop.py and replace it.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

CAPTION = re.compile(r'^\s*((?:fig(?:ure)?\.?|table|tab\.)\s*[0-9]+[a-z]?)\s*[:.\s]', re.I)


def extract_figures(pdf: Path, target: Path, dpi=200, force=False):
    import fitz
    target.mkdir(parents=True, exist_ok=True)
    notes = ['# 自动裁剪的图表索引', '',
             '> 图表定位采用 caption 和版面启发式方法，可能裁错、裁缺。讲解前必须查看 `_contact.png` 或 PDF 原页。', '']
    output_files = []
    with fitz.open(pdf) as doc:
        for page_idx, page in enumerate(doc):
            box = page.rect
            blocks = page.get_text('blocks', sort=True)
            for blk in blocks:
                if len(blk) < 5:
                    continue
                x0, y0, x1, y1, t = blk[:5]
                # Caption is usually at the beginning of its text block, not any body reference.
                m = CAPTION.match(t.replace('\n', ' ', 1))
                if not m:
                    continue
                token = re.sub('[^0-9a-zA-Z]+', '-', m.group(1).lower()).strip('-')
                kind = 'tab' if token.startswith('tab') else 'fig'
                number = re.search(r'\d+[a-z]?', token)
                number = number.group(0) if number else 'unknown'
                name = f'{kind}-{number}-p{page_idx + 1:02d}.png'
                out = target / name
                # In two-column papers, constrain to the column containing caption.
                # Wide captions generally indicate a two-column-wide figure.
                central = box.x0 + box.width / 2
                cap_width = x1 - x0
                if cap_width < box.width * 0.56:
                    left = x0 < central
                    crop_left = box.x0 + (box.width * 0.025 if left else box.width * 0.51)
                    crop_right = box.x0 + (box.width * 0.49 if left else box.width * 0.975)
                else:
                    crop_left = box.x0 + box.width * 0.025
                    crop_right = box.x1 - box.width * 0.025
                # Most figures appear directly above caption; tables sometimes below caption.
                if kind == 'tab':
                    top = max(box.y0 + 10, y0 - 30)
                    bottom = min(box.y1 - 10, max(y1 + 150, y0 + 175))
                else:
                    top = max(box.y0 + 8, y0 - min(250, box.height * 0.42))
                    bottom = min(box.y1 - 8, y1 + 8)
                if top >= bottom - 20:
                    continue
                clip = fitz.Rect(crop_left, top, crop_right, bottom) & box
                if not out.exists() or force:
                    page.get_pixmap(clip=clip, dpi=dpi, alpha=False).save(str(out))
                output_files.append(out)
                summary = re.sub(r'\s+', ' ', t).strip()[:180]
                notes.append(f'- **{name}** — PDF 第 {page_idx + 1} 页，{summary}')
                notes.append(f'  - `![]({name})`')
    if not output_files:
        notes.append('未自动定位图表 caption；请依据 PDF 页码使用 `crop.py` 手动截取重要图片。')
    (target / 'index.md').write_text('\n'.join(notes) + '\n', encoding='utf-8')
    if output_files:
        with fitz.open() as overview:
            w = 750
            tile_h = 275
            for start in range(0, len(output_files), 12):
                group = output_files[start:start + 12]
                # 2 columns × 6 rows per page; preserves original aspect ratio.
                p = overview.new_page(width=w, height=tile_h * ((len(group) + 1) // 2))
                for n, path in enumerate(group):
                    col, row = n % 2, n // 2
                    rect = fitz.Rect(col * (w / 2) + 8, row * tile_h + 28,
                                     (col + 1) * (w / 2) - 8, (row + 1) * tile_h - 8)
                    p.insert_text((col * w / 2 + 10, row * tile_h + 17), path.name, fontsize=10)
                    p.insert_image(rect, filename=str(path), keep_proportion=True)
            montage = overview[0].get_pixmap(dpi=95, alpha=False)
            montage.save(str(target / '_contact.png'))
            if len(overview) > 1:
                overview.save(str(target / '_contact.pdf'))
    return f'定位 {len(output_files)} 个图表候选（请检查 figures/_contact.png）' if output_files else '未找到可可靠定位的图表，需手动裁图'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('paper_pdf', type=Path)
    ap.add_argument('--dest', type=Path)
    ap.add_argument('--dpi', type=int, default=200)
    ap.add_argument('--force', action='store_true', help='重裁候选图表（覆盖已有同名图片）')
    a = ap.parse_args()
    if not a.paper_pdf.is_file():
        ap.error('不存在该 PDF')
    print(extract_figures(a.paper_pdf, a.dest or a.paper_pdf.parent / 'figures', dpi=a.dpi, force=a.force))


if __name__ == '__main__':
    main()
