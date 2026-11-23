# Paper Reading Skill

适用于 Codex 桌面应用的**按需论文阅读与问答** Skill，参考 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading)。

提供 PDF、LaTeX、原始图表与官方代码的获取、索引和核验。**围绕你的问题，结合论文原文、图表和代码解释架构、公式、训练、数据与实验。** 支持复用已有论文资料与按需生成交互计算可视化。

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
└── <论文名称>/       # 读新论文时由 Agent 创建，按需生成独立 HTML
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

或：`使用 $paper-reading，对着 GeoVec-VLM 的图 2 解释空间对象怎样形成。`

会检查并复用已有 **PDF、LaTeX、原始图表和官方代码**，补齐缺失材料，再依据你的具体问题查证和讲解。

## 用户自由提问

你可以直接问研究动机、原论文某张图、模块的输入输出、某项 Loss、数据样本、Batch 信息流、实验表或对应代码。回答时先解释作用与原因，再结合原论文图、公式和具体数字展开；真实数字与示意计算分开标注。

提供论文链接后，可以先准备材料并简要了解论文身份与研究主题，再继续提出感兴趣的问题。新聊天可复用已有论文目录、原始资料和阅读笔记。

## 可选的交互计算 HTML

需要**交互式 HTML 或动画计算演示**时，按照 [flow-visualization-guide.md](references/flow-visualization-guide.md) 生成独立、离线的 `信息流与维度可视化.html`。信息流解释和数值例子也可以直接在聊天中以流程图、示意图和计算步骤呈现。

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

- `SKILL.md`：材料准备、论文问答、图表与代码核验及笔记规则。
- `scripts/fetch_paper.py`：准备 PDF、文本、LaTeX、图表与已核实的官方代码。
- `scripts/extract_figures.py`：索引 LaTeX 原始图资源和表格环境，保留源码位置与宏上下文，不截图。
- `references/notes-template.md`：按实际问答记录理解与证据的笔记模板。
- `references/flow-visualization-guide.md`：用户明确要求交互 HTML 时使用的计算动画与离线验收指南。
- `profile.example.md`：可公开分享的通用阅读偏好。

## 许可与致谢

本项目采用 [MIT License](LICENSE)，保留原项目的版权声明。感谢 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 在论文精读与多材料核对方面提供的思路；此版本针对 Codex 本地项目的材料存储、原图展示与交互问答做了适配。
