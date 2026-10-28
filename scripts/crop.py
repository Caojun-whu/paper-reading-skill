#!/usr/bin/env python3
"""按需将 PDF 指定页面或相对坐标区域裁成 PNG。

  python scripts/crop.py papers/demo/paper.pdf --page 3 --output papers/demo/figures/page3.png
  python scripts/crop.py papers/demo/paper.pdf --page 3 --rect 0.1 0.2 0.9 0.7 --output papers/demo/figures/fig3.png

页码从 1 开始；--rect 为页面宽高的 0–1 比例（左 上 右 下）。
"""
import argparse
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf', type=Path)
    p.add_argument('--page', type=int, required=True, help='PDF 页码，从 1 开始')
    p.add_argument('--rect', type=float, nargs=4, default=[0, 0, 1, 1], metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    p.add_argument('--output', '-o', type=Path, required=True)
    p.add_argument('--dpi', type=int, default=220)
    a = p.parse_args()
    try:
        import fitz
    except ImportError:
        raise RuntimeError('需要 PyMuPDF：pip install pymupdf')
    if not a.pdf.is_file():
        raise ValueError(f'找不到 PDF：{a.pdf}')
    l,t,r,b = a.rect
    if not (0 <= l < r <= 1 and 0 <= t < b <= 1):
        raise ValueError('裁剪范围应满足 0<=左<右<=1 且 0<=上<下<=1')
    if a.dpi < 72 or a.dpi > 600:
        raise ValueError('建议 dpi 在 72–600 之间')
    with fitz.open(a.pdf) as doc:
        if not 1 <= a.page <= len(doc):
            raise ValueError(f'页码应为 1–{len(doc)}')
        page = doc[a.page - 1]
        bounds = page.rect
        clip = fitz.Rect(bounds.x0 + bounds.width*l, bounds.y0 + bounds.height*t,
                         bounds.x0 + bounds.width*r, bounds.y0 + bounds.height*b)
        pix = page.get_pixmap(clip=clip, dpi=a.dpi, alpha=False)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(a.output))
    print(f'已保存：{a.output.resolve()}')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError) as e:
        print(f'错误：{e}', file=sys.stderr)
        sys.exit(1)
