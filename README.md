# Paper Reading Skill

适用于 Codex 桌面应用的六站式论文精读 Skill，参考 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading)。

按 **动机 → 架构 → 训练 → 数据 → 信息流 → 具体案例** 逐站交互讲解，交叉核对 PDF、LaTeX、图表与可核实的官方代码，并保存可跨会话继续的精读笔记。默认不运行论文代码或复现实验。

## 环境

- Codex 桌面应用，或可加载 `SKILL.md` 并操作本地文件的 Codex 环境。
- Python 3.10+、Git；脚本依赖 PyMuPDF，详见 `requirements.txt`。
- 获取在线论文、arXiv 源码及官方代码时需要网络；本地 PDF 也可使用。

## 安装（只安装一次）

在当前 Codex 项目的根目录运行：

```bash
mkdir -p .agents/skills
git clone https://github.com/Caojun-whu/paper-reading-skill.git .agents/skills/paper-reading
python3 -m pip install -r .agents/skills/paper-reading/requirements.txt
```

也可下载仓库 ZIP，解压后将文件夹重命名为 `paper-reading`，再放入 `.agents/skills/`。安装后的结构：

```text
当前项目/
├── .agents/
│   └── skills/
│       └── paper-reading/
│           ├── SKILL.md
│           ├── profile.example.md
│           ├── references/
│           └── scripts/
└── <论文名称>/       # 读新论文时由 Agent 创建
```

Skill 的安装目录与论文资料目录是两件事。**每篇论文直接建在当前项目下**，不另外套一层 `papers/`。

安装完成后开启新会话，让 Codex 发现 Skill。若当前项目也由 Git 管理，上述克隆会形成嵌套仓库；需要将 Skill 文件纳入项目版本管理时，可使用 ZIP 安装方式。

## 自定义阅读偏好

默认使用通用的 `profile.example.md`。如需个人设置：

```bash
cp .agents/skills/paper-reading/profile.example.md .agents/skills/paper-reading/profile.md
```

修改 `profile.md` 即可。该文件已加入 `.gitignore`；请勿将个人背景、未公开研究资料或密钥写入公开文件。

## 使用

在 Codex 桌面应用的新会话中说：

```
使用 $paper-reading 精读这篇论文：https://arxiv.org/abs/xxxx.xxxxx
```

或：`使用 $paper-reading，继续刚才的 Geo2Vec。`

会尽可能获取 **PDF、LaTeX、图表、官方代码**，先核实材料，再按 **动机 → 架构 → 训练 → 数据 → 信息流 → 具体案例** 六站交互讲解。默认不运行官方代码或复现实验。

## 脚本（Agent 可以自动执行）

首次读取时，在项目目录执行：

```bash
python3 -m pip install -r .agents/skills/paper-reading/requirements.txt  # 仅缺 PyMuPDF 时
python3 .agents/skills/paper-reading/scripts/fetch_paper.py 2410.24164 --dest '论文名称'
```

核实官方仓库后补下载代码：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py '论文名称' --code 'https://github.com/author/official-repo'
```

图直接使用 LaTeX 引用的原始文件，不从论文页面截图。`figures/index.md` 记录原图路径、图注、label 和源文件位置；组合图同时保留完整 figure 环境，避免漏掉子图标记或正文式注释。

表格保留完整 LaTeX 环境及宏定义位置，见 `tables/index.md`。讲解时按需整理成 Markdown，保留多级表头、单位、缺失值和脚注；复杂表不默认自动转换或截图。关键数值与实际编号仍以原 PDF 交叉核对。

已有论文只更新图表索引，无需重新下载：

```bash
python3 .agents/skills/paper-reading/scripts/extract_figures.py '论文名称'
```

此命令仅生成源码索引和阅读片段，不修改原始图片。没有 LaTeX 或独立图文件时如实标记；需要在聊天中展示独立 PDF 原图时，可完整渲染该文件，不截取论文页面。

论文名称来源于真实标题或常用简称，Agent 自行确定并作为 `--dest` 参数传入。已有论文目录原样复用，不覆盖笔记。未提供可确认的官方实现时，应如实说明。

## 文件说明

- `SKILL.md`：六站阅读流程、材料核对与断点续读规则。
- `scripts/fetch_paper.py`：准备 PDF、文本、LaTeX、图表与已核实的官方代码。
- `scripts/extract_figures.py`：索引 LaTeX 原始图资源和表格环境，保留源码位置与宏上下文，不截图。
- `references/notes-template.md`：精读笔记模板。
- `profile.example.md`：可公开分享的通用阅读偏好。

## 许可与致谢

本项目采用 [MIT License](LICENSE)，保留原项目的版权声明。感谢 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 提供的六站精读及多材料核对思路；此版本针对 Codex 本地项目的材料存储、交互和续读流程做了适配。
