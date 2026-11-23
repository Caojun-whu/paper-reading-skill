---
name: paper-reading
description: 收集和整理单篇学术论文的本地材料，包括 PDF、arXiv LaTeX 源码、原始图表资源与表格索引、已核实的官方代码。适用于用户提供 arXiv 链接或 ID、PDF 链接、本地 PDF、已有论文目录，或要求准备、检查、补齐论文资料时。优先复用已有文件，按需补齐缺项。
---

# Paper Reading · 论文材料收集

**职责：将论文的原始资料及可检索索引整理到 Codex 当前项目中，复用已有文件，补齐缺少的材料，并报告资料状态。**

## 1. 保存目录

在 **Codex 当前打开的项目根目录**，直接使用一个以论文标题或清晰简称命名的文件夹，例如 `GeoVec-VLM/`。每篇论文固定对应一个目录。创建前检查是否已有同一论文的资料目录；存在则复用，不另建嵌套的 `papers/` 或其他目录，不覆盖用户已有文件。

目录中按实际可获取的材料组织：

```text
<论文名称>/
├── paper.pdf          # 论文原始 PDF
├── source/            # arXiv 原始 LaTeX 及图表资源
├── paper.tex          # 便于检索的展开版 LaTeX
├── paper.txt          # PDF 逐页提取的文字
├── outline.md         # 章节与源码位置索引
├── meta.json          # 论文元数据与材料状态
├── figures/           # 原始 figure 资源索引（图片保留在 source/）
├── tables/            # 原始 table 环境与宏的索引
└── code/              # 已核实的官方代码（如公开）
```

缺失或未公开的资源在状态报告中说明，不生成空文件或伪造资料。**保留目录中用户另行保存的笔记、图或其他文件。**

## 2. 下载和补齐材料

以下 `<skill>` 表示本 `SKILL.md` 所在目录。命令从 **Codex 当前项目根目录**执行。

首次获取论文：

```bash
python3 <skill>/scripts/fetch_paper.py "<arXiv 链接/ID、PDF 链接或本地 PDF>" --dest "<论文名称>"
```

复用已有论文目录、检查并补齐材料：

```bash
python3 <skill>/scripts/fetch_paper.py "<已有论文目录>"
```

已核实官方仓库后补充代码：

```bash
python3 <skill>/scripts/fetch_paper.py "<已有论文目录>" --code "https://github.com/author/official-repo"
```

依赖为 Python 3、Git、PyMuPDF；确实缺少 PyMuPDF 时安装 `python3 -m pip install -r <skill>/requirements.txt`。新论文的 `--dest` 是项目根目录下**单层文件夹名称**，不要传绝对路径或任意嵌套路径。

获取与补齐时按以下要求检查：

1. **论文身份与 PDF**：只收到名称时先核实标题、作者、版本和链接；有同名论文时确认对应作品。保存 `paper.pdf`；已有非空 PDF 时直接复用。记录 arXiv ID、版本与已确认的元信息。
2. **LaTeX 源码**：尽可能获取公开的 arXiv 原始源码到 `source/`，生成便读的 `paper.tex`、PDF 文字 `paper.txt` 和章节索引 `outline.md`。保留原始源码及宏，展开版仅供检索，不替代原始 LaTeX。
3. **原始图表和表格**：运行现有图表索引逻辑，保留 `figure/table` 环境、原始资源路径、图注/表注、label、源文件行号及宏定义位置。原图以 `source/` 内的 PDF/PNG/JPG 等资源为准，**不从论文页面截图或自动裁图来替代原图**；多子图要保留完整环境。表格索引保留多级表头、合并单元格、单位、脚注及缺失值等源码信息，重要对应关系与 `paper.pdf` 核对。
4. **官方代码**：优先核实论文中的代码声明、项目页、作者主页与仓库 README，确认官方归属后使用 `--code` 浅克隆到 `code/`。第三方复现、被引用的其他仓库不当作官方实现；不存在或无法确认时注明。已有 `code/` 不覆盖。
5. **检查状态**：读取已有 `meta.json` 和真实文件，确认哪些已获取、哪些缺失或失败。已有资源尽量复用，只补必要缺项；没有源码时仍保留 PDF 与可用的索引/状态。不要将静态索引当作人工目视核验的证明。

已有 LaTeX 源码仅需要更新图表和表格索引时：

```bash
python3 <skill>/scripts/extract_figures.py "<论文目录>"
```

此脚本索引原始 LaTeX 图表资源与源码环境，不修改原始图文件。

## 3. 完成后的交付

简要报告：**论文标题/版本、资料目录、PDF/LaTeX/图表索引/官方代码各自的状态，以及缺失项或失败原因**。需要时给出实际文件路径，方便后续直接使用。

## 安全边界

仅下载公开论文及已核实的官方代码。对克隆的仓库**只读取文件**；不执行仓库脚本、安装其依赖、下载大模型权重或启动训练/复现实验，除非用户另行要求。保留现有用户文件，不覆盖人工修改的资料。

## 参考与许可

参考 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 的论文资料获取思路，保留原项目版权与 [MIT License](LICENSE)。
