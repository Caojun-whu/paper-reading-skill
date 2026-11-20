# Paper Reading Skill

适用于 Codex 桌面应用的七站式论文精读 Skill，参考 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading)。

按 **动机 → 架构 → 训练 → 数据 → 信息流 → 具体案例 → 实验与结果** 逐站交互讲解，交叉核对 PDF、LaTeX、图表与可核实的官方代码，并保存可跨会话继续的精读笔记。默认不运行论文代码或复现实验。

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
└── <论文名称>/       # 读新论文时由 Agent 创建，⑤站生成独立 HTML
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

会尽可能获取 **PDF、LaTeX、图表、官方代码**，先核实材料，再按 **动机 → 架构 → 训练 → 数据 → 信息流 → 具体案例 → 实验与结果** 七站交互讲解。默认不运行官方代码或复现实验。

## 第⑤站：交互式信息流与维度可视化

阅读到第⑤站时，Agent 除了讲解输入如何经过各个模块，还应在当前论文目录生成 **`信息流与维度可视化.html`**。直接双击即可在浏览器打开；这是针对**当前论文**创作的单文件交互式讲解，不需要启动本地服务器或安装 React 项目。

**形式由 AI 根据论文机制自主设计**，不限定统一的流程图模板：例如 CNN 的特征图尺度变化、Transformer 注意力矩阵、多模态数据的并行路径与融合、GNN 的消息传播或扩散模型的去噪迭代。鼓励有教学意义的动态演示、清晰生动的视觉隐喻、局部展开与逐步播放；若 2D 更易理解就用 SVG/Canvas，确有必要才采用 Three.js/WebGL。**美观不能牺牲机制和维度的准确性**。

页面至少包含：整体执行路径、逐步/暂停/前后步/重置控制、可查看模块细节的交互、关键张量名称与完整 shape、维度流转表、论文/官方代码依据及未知项标记；训练/推理分支、循环与缓存等按论文实际机制展示。若使用示意数值、非等比例形状或高维张量投影，需显式说明。生成的图是教学示意，**不替代论文原始图表，也不从 PDF 页面截图或裁图**。

单文件应内嵌 HTML/CSS/JavaScript、数据和必需依赖，不依赖在线 CDN、外部请求或 `file://` 下受限的资源加载；如果需要 Three.js，应将所需代码合法地内嵌或改用原生 SVG/Canvas。Agent 应检查生成文件能否离线打开、交互是否工作，并把路径及待核验维度记入笔记；无法测试时注明测试限制。详细设计与验收规范见 [flow-visualization-guide.md](references/flow-visualization-guide.md)。

## 第⑦站：实验与结果

第⑦站为必读：先梳理论文实际开展的实验及各自目的，再逐组讲清 **实验如何设计、用了哪些数据集及划分、比较了哪些 baseline、采用哪些指标与评测设置、得到了什么具体结果**，最后评估实验能否支持作者的核心主张。主实验、消融、泛化、鲁棒性、效率和失败案例等按论文实际报告的范围讲解；内容多时在本节内分多轮推进。

实验表格优先从 `tables/index.md` 定位原始 LaTeX 表格及宏上下文，保留多级表头、合并单元格、单位、脚注和缺失值，并与 PDF 核对编号及重要数值；实验曲线和可视化优先使用 `figures/index.md` 对应的 LaTeX 原始图资源，**不从论文 PDF 截图或裁图替代原图**。缺少源码则据 PDF 明确标注页码，不虚构结果或对应关系。重要结论标注【论文】【官方代码】【分析】，并记录到精读笔记。

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

- `SKILL.md`：七站阅读流程、材料核对与断点续读规则。
- `scripts/fetch_paper.py`：准备 PDF、文本、LaTeX、图表与已核实的官方代码。
- `scripts/extract_figures.py`：索引 LaTeX 原始图资源和表格环境，保留源码位置与宏上下文，不截图。
- `references/notes-template.md`：精读笔记模板。
- `references/flow-visualization-guide.md`：第⑤站交互式 HTML 的选型、视觉规范与离线验收说明。
- `profile.example.md`：可公开分享的通用阅读偏好。

## 许可与致谢

本项目采用 [MIT License](LICENSE)，保留原项目的版权声明。感谢 [skJack/kelip-paper-reading](https://github.com/skJack/kelip-paper-reading) 提供的七站精读及多材料核对思路；此版本针对 Codex 本地项目的材料存储、交互和续读流程做了适配。
