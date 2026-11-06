# Paper Reading Skill

面向 Codex 的**AI 主导、工具优先**六站式论文精读 Skill。参考 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading)，以 **研究动机 → 模型架构 → 数据与监督 → 训练与优化 → 推理与信息流 → 案例与证据检验** 进行交互式教学，保留证据核查与断点续读。

> **唯一工作模式：完整六站精读。** 每次使用 Skill 都先主动尝试保存 PDF、公开的 LaTeX 原始源码和已核实的官方代码（续读时补齐缺项），再逐站讲解。AI 自主选择搜索、PDF 视觉、下载和文件工具，不强制运行 Python 脚本；材料准备要求不会因当前提问只涉及某一部分而取消。

## 核心原则

- **AI 负责研究判断**：确认论文和版本、理解正文与图表、判断代码是否官方、追踪方法的数据流。
- **优先原生工具**：使用 Codex 环境已有的搜索、PDF 视觉、文件读写和代码浏览工具；不假定任何工具在所有环境均可用。
- **脚本可选**：下载、解包源码、批量文本准备、自动裁图与精确裁剪只是备选工作流。
- **统一资料基线**：有可写目录时，开始第一站前主动尝试获取 PDF、公开 TeX Source 和论文/作者确认的官方代码，并记录成功或失败；续读先核查并补齐缺项。未公开或下载受限不阻止有证据支持的六站讲解。
- **只提供完整六站流程**：即使用户想重点理解某个公式或模块，也在对应站重点解释，不另设跳过资料准备的单点答疑模式。
- **每轮只讲一站**：用户说“继续”才进入下一站；可在当前站追问，始终保留完整六站的进度记录。
- **理解与判断并重**：先理解样本与监督，再解释优化；用完整案例验证方法理解，并检查实验、消融或证明能支持什么结论。
- **适应论文类型**：默认流程适合算法/深度学习；理论、系统、数据集和综述论文可替换不适用的训练/张量内容，而不硬套术语。
- **不执行论文代码**：默认只静态阅读代码，不安装论文环境、不下载大规模权重、不复现实验。
- **如实说明限制**：未取得的材料、未验证的图、无法保存的笔记不能声称已经处理完成。

具体行为见 [SKILL.md](SKILL.md)，按需读取 [资料与证据规范](references/materials-and-evidence.md) 和 [六站教学细则](references/six-stations.md)。

## 六站怎么分工

| 站点 | 重点 |
| --- | --- |
| ① 研究动机 | 问题、旧方法的不足与作者假设 |
| ② 模型架构 | **静态视角**：有哪些模块、为什么这样设计 |
| ③ 数据与监督 | 一条真实样本及其标签、监督信号 |
| ④ 训练与优化 | 对应③的样本，解释损失、训练策略和参数更新 |
| ⑤ 推理与信息流 | **动态视角**：执行顺序、关键张量和运行时状态 |
| ⑥ 案例与证据检验 | **完整案例为主**；再简要检验强基线、消融、成本及局限 |

第⑥站的两个部分可以在**同一站内分多轮**，不强制新增第七站。没有实验或证明材料时标记未核实，不凭空补全。理论论文可侧重证明条件，系统论文侧重工作负载及性能，数据集论文侧重质量/偏差，综述论文侧重筛选范围和比较依据。

已有旧版笔记中③为训练、④为数据；**续读时按笔记标题和内容判断进度**，不得仅凭编号重排或覆盖已有记录。

## 使用前提

- 支持加载 `SKILL.md` 的 Codex 桌面应用或兼容环境。
- 当前环境提供的搜索、文件、PDF 和代码工具越完整，可直接完成的操作越多；并非所有功能都依赖脚本。
- **持久化笔记需要一个可写的项目目录**。如果环境不能写文件，AI 可以在当前对话中讲解，但不能声称已保存可跨会话恢复的笔记。
- **Python、Git、PyMuPDF 仅在使用对应脚本时需要**；普通安装无需预先执行 `pip install`。

## 安装（只安装一次）

在当前 Codex 项目的根目录运行：

```bash
mkdir -p .agents/skills
git clone https://github.com/Caojun-whu/paper-reading-skill.git .agents/skills/paper-reading
```

也可以下载 ZIP，解压后重命名为 `paper-reading` 并放在 `.agents/skills/`。

```text
当前项目/
├── .agents/
│   └── skills/
│       └── paper-reading/
│           ├── SKILL.md
│           ├── profile.example.md
│           ├── references/
│           └── scripts/          # 可选辅助工具
└── <论文简称>/                 # 如需保存资料/笔记，由 Agent 创建
```

安装后开启新会话，让 Codex 发现 Skill。Skill 安装目录与论文资料目录是两回事；每篇论文直接放在当前项目根目录下，不额外创建 `papers/`。如果主项目也是 Git 仓库，直接克隆会形成嵌套仓库；想把 Skill 文件纳入主项目版本管理时推荐 ZIP 安装。

## 怎么使用

在 Codex 中输入：

```text
使用 $paper-reading 精读这篇论文：
https://arxiv.org/abs/xxxx.xxxxx
```

也可以说：

```text
使用 $paper-reading，继续上次的 Geo2Vec。
```

如果提出“重点解释这篇论文的训练损失”，Skill 仍先建立 PDF / LaTeX / 官方代码资料基线，然后按六站推进；到④训练与优化时着重深入损失函数，不设置仅回答公式的快捷模式。

每次首次阅读（包括“请为我讲解这篇论文”）时，AI 先核实论文身份，在可写目录下**主动尝试**获取 PDF、论文公开的原始 LaTeX 源文件与已核实的官方代码，再简短报告材料清单及缺失/失败原因，然后进入**① 研究动机**。续读时核查并补齐未获取的材料。此时不必事先完全消化代码，但不能因为第一站暂时不需要就跳过获取尝试。需要解读架构图时应实际查看原论文 PDF 页，不能只展示未经核验的自动裁图。

**来源不只 GitHub**：有些论文把官方代码发布在 Figshare、Zenodo 或 OSF。对于这种来源，AI 应找到真实文件下载入口并尝试安全保存，而不是尝试 Git 克隆或仅提供页面链接。资料入口无法访问、文件过大或没有公开源码时，记录状态并继续可核实内容。

## 脚本：按需使用，不是必经步骤

| 文件 | 什么时候才考虑使用 |
| --- | --- |
| `scripts/fetch_paper.py` | 原生工具不便于可靠保存 PDF、批量提取文本或解包 arXiv LaTeX 时 |
| `scripts/extract_figures.py` | 需要批量获得图表候选且无法方便地直接查看/裁剪原页时 |
| `scripts/crop.py` | 需要把 PDF 的指定页面/区域保存为精确 PNG 时 |

仅在确实需要运行脚本且缺 PyMuPDF 时，经允许安装其依赖：

```bash
python3 -m pip install -r .agents/skills/paper-reading/requirements.txt
```

例如，需要由辅助脚本保存 PDF、文本及公开的 arXiv LaTeX 源文件时（不跳过 TeX）：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py \
  2410.24164 --dest "论文简称" --no-figures --no-code
```

不使用 `--no-tex` 跳过公开源码的获取尝试。如需脚本克隆**已核实的 GitHub/GitLab 官方代码**，才执行：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py \
  "论文简称" --code "https://github.com/author/official-repo" --no-figures
```

**`fetch_paper.py --code` 仅支持 GitHub/GitLab**。对于 Figshare、Zenodo、OSF 等归档，AI 需借助当前工具找到实际文件 URL，检查文件类型、规模和解压安全性，再保存到 `code/`；不能将分享页 HTML 当作代码包。所有自动裁剪图必须与 PDF 原页核对。若生成 `figures/_contact.pdf`，还应检查其中的后续页，不能只看 `_contact.png`。无需裁图时直接使用 PDF 视觉工具即可。

## 自定义偏好与笔记

如需自定义：

```bash
cp .agents/skills/paper-reading/profile.example.md \
  .agents/skills/paper-reading/profile.md
```

可设置讲解深度、例子与术语偏好等。个人 `profile.md` 已加入 `.gitignore`，不要把隐私信息或密钥提交到公开仓库。

有可写项目目录时，阅读记录按 [笔记模板](references/notes-template.md) 增量保存在每篇论文的 `精读笔记.md` 中，记录 **PDF / LaTeX / 官方代码的实际取得状态**、当前站、关键证据、问答及下一步；再次阅读时先读取已有笔记，兼容旧版站点顺序且不覆盖人工笔记。没有本地持久化能力时不会假装已保存。

## 文件导览

- [SKILL.md](SKILL.md)：触发、工具策略、六站调度、证据及安全边界。
- [references/materials-and-evidence.md](references/materials-and-evidence.md)：按需获取材料、可选脚本、安全与来源管理。
- [references/six-stations.md](references/six-stations.md)：六站详细教学标准。
- [references/notes-template.md](references/notes-template.md)：精读笔记模板。
- [profile.example.md](profile.example.md)：通用阅读偏好。
- [evals/materials-acquisition.md](evals/materials-acquisition.md)：针对 arXiv 源码和非 GitHub 官方代码的人工回归验收案例。
- `scripts/`：可选的 PDF/LaTeX/图表辅助处理工具。

## 许可与致谢

本项目采用 [MIT License](LICENSE)，保留原项目版权声明。感谢 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 提供的六站精读与多材料核对思路。
