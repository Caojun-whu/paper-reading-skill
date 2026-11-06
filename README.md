# Paper Reading Skill

面向 Codex 的**AI 主导、工具优先**六站式论文精读 Skill。参考 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading)，以 **动机 → 架构 → 训练 → 数据 → 信息流 → 具体案例** 进行交互式教学，保留证据核查与断点续读。

> **v2 核心变化：不再把 Python 脚本当作论文阅读的必经入口。** AI 根据当前工具能力和问题决定是否需要搜索、查看 PDF 原页、检查 LaTeX 与官方代码。只有原生工具不适合完成特定文件操作时，才按需使用仓库内的辅助脚本。

## 核心原则

- **AI 负责研究判断**：确认论文和版本、理解正文与图表、判断代码是否官方、追踪方法的数据流。
- **优先原生工具**：使用 Codex 环境已有的搜索、PDF 视觉、文件读写和代码浏览工具；不假定任何工具在所有环境均可用。
- **脚本可选**：下载、解包源码、批量文本准备、自动裁图与精确裁剪只是备选工作流。
- **按需补齐证据**：当前站需要什么就核实什么；缺失 LaTeX 或官方代码不应阻止解释有证据支持的内容。
- **每轮只讲一站**：用户说“继续”才进入下一站，也可以按需求追问或跳站。
- **不执行论文代码**：默认只静态阅读代码，不安装论文环境、不下载大规模权重、不复现实验。
- **如实说明限制**：未取得的材料、未验证的图、无法保存的笔记不能声称已经处理完成。

具体行为见 [SKILL.md](SKILL.md)，按需读取 [资料与证据规范](references/materials-and-evidence.md) 和 [六站教学细则](references/six-stations.md)。

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

或者直接询问论文特定问题，例如“解释这篇论文的训练损失”。局部问题会优先定位相关证据，不必每次走完整六站。

完整精读时，AI 先核实论文身份和足够的原始材料，给出简短基本情况，然后进入**① 动机**；用户继续时再讲后续站点。需要解读架构图时应实际查看原论文 PDF 页，不能只展示未经核验的自动裁图。

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

例如，仅需要脚本准备 PDF 和文本，而其他材料打算由 AI 按需检查时：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py \
  2410.24164 --dest "论文简称" --no-tex --no-figures --no-code
```

如果确实需要 arXiv 源码，再省略 `--no-tex`；如需官方代码，**先核实代码归属**，然后按需执行：

```bash
python3 .agents/skills/paper-reading/scripts/fetch_paper.py \
  "论文简称" --code "https://github.com/author/official-repo"
```

所有自动裁剪图必须与 PDF 原页核对。若生成 `figures/_contact.pdf`，还应检查其中的后续页，不能只看 `_contact.png`。无需裁图时直接使用 PDF 视觉工具即可。

## 自定义偏好与笔记

如需自定义：

```bash
cp .agents/skills/paper-reading/profile.example.md \
  .agents/skills/paper-reading/profile.md
```

可设置讲解深度、例子与术语偏好等。个人 `profile.md` 已加入 `.gitignore`，不要把隐私信息或密钥提交到公开仓库。

有可写项目目录时，阅读记录按 [笔记模板](references/notes-template.md) 增量保存在每篇论文的 `精读笔记.md` 中，记录当前站、重要解释、问答及下一步；再次阅读时先读取已有笔记。没有本地持久化能力时不会假装已保存。

## 文件导览

- [SKILL.md](SKILL.md)：触发、工具策略、六站调度、证据及安全边界。
- [references/materials-and-evidence.md](references/materials-and-evidence.md)：按需获取材料、可选脚本、安全与来源管理。
- [references/six-stations.md](references/six-stations.md)：六站详细教学标准。
- [references/notes-template.md](references/notes-template.md)：精读笔记模板。
- [profile.example.md](profile.example.md)：通用阅读偏好。
- `scripts/`：可选的 PDF/LaTeX/图表辅助处理工具。

## 许可与致谢

本项目采用 [MIT License](LICENSE)，保留原项目版权声明。感谢 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 提供的六站精读与多材料核对思路。
