# Paper Reading Skill · 论文材料收集

Codex 的论文资料准备 Skill：**获取并整理 PDF、arXiv LaTeX 源码、原始图表、表格索引和已核实的官方代码**，并复用已经下载到项目中的材料。

## 环境

- Codex 桌面应用，或支持 `SKILL.md` 并能访问当前项目文件的 Codex 环境。
- Python 3.10+、Git、PyMuPDF（依赖见 `requirements.txt`）。
- 下载公开论文、arXiv 源码及官方仓库需要网络，本地 PDF 也可使用。

## 安装

在当前 Codex 项目根目录执行：

```bash
mkdir -p .agents/skills
git clone https://github.com/Caojun-whu/paper-reading-skill.git .agents/skills/paper-reading
python3 -m pip install -r .agents/skills/paper-reading/requirements.txt
```

也可以下载 ZIP 并放到 `.agents/skills/paper-reading/`。Skill 的安装目录与论文资料目录分开；每篇论文的资料文件夹直接建立在**项目根目录**下。

## 使用

在 Codex 中说：

```text
使用 $paper-reading，收集这篇论文的材料：https://arxiv.org/abs/xxxx.xxxxx
```

或：

```text
使用 $paper-reading，检查 GeoVec-VLM/ 的材料并补齐缺少的文件。
```

Skill 会检查已有文件，准备 PDF、LaTeX、原始图表与表格索引、已核实的官方代码，最后报告目录和获取状态。

## 资料目录

```text
当前项目/
├── .agents/skills/paper-reading/
└── <论文名称>/
    ├── paper.pdf          # 原始 PDF
    ├── source/            # LaTeX 及原图、表格资源
    ├── paper.tex          # 展开版源码（检索用）
    ├── paper.txt          # 按页提取的 PDF 文字
    ├── outline.md         # 章节及行号
    ├── meta.json          # 元数据与材料状态
    ├── figures/           # 原始图资源与 figure 索引
    ├── tables/            # table 环境与宏索引
    └── code/              # 已核实的官方代码
```

目录中保留已存在的其他文件。尚未公开或获取失败的资源在状态中注明。

## 脚本

首次获取：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py 2410.24164 --dest "论文名称"
```

复用已有目录：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py "论文名称"
```

核实官方仓库后获取代码：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py "论文名称" --code "https://github.com/author/official-repo"
```

仅更新现有 LaTeX 图表与表格索引：

```bash
python3 .agents/skills/paper-reading/scripts/extract_figures.py "论文名称"
```

`fetch_paper.py` 处理 PDF、LaTeX、文字索引及官方代码；`extract_figures.py` 索引原始 LaTeX 的 figure/table 环境和文件位置。图像来自 `source/` 的原始文件，**不从论文 PDF 页面截图或裁图替代**。下载源码时会保留 LaTeX 宏和相关资源，表格索引与 PDF 核对。

## 文件说明

- `SKILL.md`：材料目录、获取和补齐规则。
- `scripts/fetch_paper.py`：论文 PDF、LaTeX、文字与官方代码准备。
- `scripts/extract_figures.py`：原始图表与表格索引。
- `requirements.txt`：Python 依赖。

## 许可与致谢

本项目采用 [MIT License](LICENSE)，保留原始版权声明。感谢 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 提供论文资料收集与多源核对的基础思路。
