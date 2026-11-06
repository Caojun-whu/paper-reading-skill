"""Behavior checks for source-only figure/table collection; no network or TeX."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from extract_figures import source_index


class SourceIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.paper = Path(self.tmp.name)
        self.source = self.paper / 'source'
        self.source.mkdir()

    def write(self, name, content):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def items(self, folder):
        return json.loads((self.paper / folder / 'index.json').read_text())['items']

    def test_composite_figures_and_table_context_survive_includes(self):
        self.write('assets/panel.pdf', 'original asset bytes')
        self.write('assets/second.png', 'original second asset bytes')
        self.write('main.tex', r'''\documentclass{article}
\graphicspath{{assets/}}
\newcommand{\resultheader}{Method & Accuracy (\%)}
\renewcommand{\arraystretch}{1.2}
\begin{document}
% \begin{figure}\includegraphics{ignored}\end{figure}
\iffalse
\begin{figure}\includegraphics{old-draft}\end{figure}
\else
\input{parts/figure}
\fi
\input{parts/table}
\end{document}
''')
        self.write('parts/figure.tex', r'''\begin{figure*}
\includegraphics[width=.4\linewidth,trim={1 2 3 4},clip]{panel}
\input{parts/second}
Text accompanying the panels: 95\%.
\caption[Short]{A \textbf{nested {caption}} with 95\% coverage.}
\label{fig:combined}
\end{figure*}
''')
        self.write('parts/second.tex', r'\includegraphics{second.png}')
        self.write('parts/table.tex', r'''\begin{table}
\renewcommand{\arraystretch}{0.9}
\caption{Results; -- means missing, not zero.}\label{tab:results}
\begin{tabular}{lr}
\resultheader \\
\multicolumn{2}{c}{Group} \\
\multirow{2}{*}{Model} & 90 \\
 & -- \\
\end{tabular}
\end{table}
''')
        before = {p: p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        (self.paper / '精读笔记.md').write_text('user notes', encoding='utf-8')
        source_index(self.paper)
        figures, tables = self.items('figures'), self.items('tables')
        self.assertEqual(len(figures), 1)
        self.assertEqual(len(tables), 1)
        fig = figures[0]
        self.assertEqual([a['path'] for a in fig['assets']], ['source/assets/panel.pdf', 'source/assets/second.png'])
        self.assertEqual(fig['assets'][1]['source'], 'source/parts/second.tex')
        self.assertEqual(fig['captions_tex'], [r'A \textbf{nested {caption}} with 95\% coverage.'])
        excerpt = (self.paper / fig['excerpt']).read_text()
        self.assertIn('Text accompanying the panels', excerpt)
        self.assertIn(r'\includegraphics{second.png}', excerpt)
        self.assertEqual([x['command'] for x in tables[0]['macro_context']], [r'\resultheader'])
        table = (self.paper / tables[0]['excerpt']).read_text()
        for content in (r'\multicolumn', r'\multirow', '-- means missing', '\\resultheader'):
            self.assertIn(content, table)
        first = (self.paper / 'figures/index.json').read_bytes()
        source_index(self.paper)
        self.assertEqual(first, (self.paper / 'figures/index.json').read_bytes())
        self.assertEqual(before, {p: p.read_bytes() for p in self.source.rglob('*') if p.is_file()})
        self.assertEqual((self.paper / '精读笔记.md').read_text(), 'user notes')
        self.assertFalse(list((self.paper / 'figures').glob('*.png')))

    def test_missing_macro_paths_and_source_drawings_are_not_guessed(self):
        self.write('main.tex', r'''\documentclass{article}
\begin{figure}
\includegraphics{missing.pdf}\includegraphics{\assetdir/panel.pdf}
\caption{Unresolved}\label{fig:missing}
\end{figure}
\begin{figure}\begin{tikzpicture}drawing\end{tikzpicture}
\caption{Source drawing}\label{fig:drawing}\end{figure}
''')
        source_index(self.paper)
        figures = self.items('figures')
        self.assertEqual([a['status'] for a in figures[0]['assets']], ['missing', 'unresolved'])
        self.assertEqual(figures[1]['assets'], [])
        self.assertFalse(list((self.paper / 'figures').glob('*.png')))

    def test_without_latex_does_not_fall_back_to_pdf_cropping(self):
        (self.paper / 'paper.pdf').write_bytes(b'not opened by source indexing')
        result = source_index(self.paper)
        self.assertIn('无可用 LaTeX', result['figures_status'])
        self.assertFalse((self.paper / 'figures').exists())

    def test_fetch_command_uses_source_index_with_existing_local_source(self):
        import pymupdf
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((72, 72), 'A local paper fixture')
            pdf.save(self.paper / 'paper.pdf')
        self.write('main.tex', r'\documentclass{article}\begin{figure}\caption{Drawing}\end{figure}')
        run = subprocess.run([sys.executable, str(SCRIPTS / 'fetch_paper.py'), str(self.paper),
                              '--no-tex', '--no-code'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        meta = json.loads((self.paper / 'meta.json').read_text())
        self.assertEqual(meta['visual_material_mode'], 'latex_source')
        self.assertEqual(len(self.items('figures')), 1)
        self.assertFalse(list((self.paper / 'figures').glob('*.png')))


if __name__ == '__main__':
    unittest.main()
