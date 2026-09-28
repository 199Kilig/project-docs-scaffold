# project-docs-scaffold

> 让 AI 写出来的项目文档可定位、可校验、可沉淀。

面向 vibe coding（AI 辅助开发）的**项目文档治理脚手架**。它给项目装上一套文档体系：**类型化的文档 + 给 AI 读的约束 + 能拦下违规提交的校验闸门**。

核心机制全部**工具无关**——Markdown + 一个 Python 校验脚本 + Git hooks，不绑定任何 AI 编码工具。

---

## Before / After

**失控的 AI 文档**（很常见的样子）：

```
docs/
├── 项目总结final.md      ← 需求 + 方案 + 决策 + 复盘 四合一
├── 需求v2.md             ← 文件名看不出讲什么
├── 设计(新).md
├── 进度-最新.md
├── notes.md              ← 草稿、快照、临时输出混在一起
└── temp2.md
```

**治理后**：

```
docs/
├── README.md                              # 文档地图（每份文档必须在此登记，双向校验）
├── docs-guide.md                          # 文档宪法：写任何文档前先读
├── 01-需求/PRD-打卡功能.md                  # 做什么、为什么做、验收标准
├── 02-方案/DESIGN-打卡功能架构.md            # 怎么做
├── 03-决策/ADR-001-选用SQLite.md            # 为什么这么选（只增不改）
├── 04-进度/PROGRESS-2026-08-30-完成骨架.md   # 本阶段发生了什么变化
├── 05-复盘/RETRO-第一轮复盘.md               # 学到了什么
├── 06-知识/                                # 我学会了什么（个人知识资产）
│   ├── README.md                          # tech-index 台账：面试前只扫这张表
│   └── TECH-SQLAlchemy-动态筛选器.md
└── _inbox/                                # 过程产物暂存区，不进 git，蒸馏后清空
```

差别不只是"摆放整齐"：**目录即类型**（一份文档只能是一类，跨界就得拆），**文件名即语义**（`PRD-打卡功能.md` 一眼知道讲什么），**每个文件都得在文档地图里登记**——没登记、或登记了却不存在，校验器直接拦下。

---

## 30 秒上手

把这个仓库作为 skill 装给你的 AI 编码助手，然后说一句话：

> **「给这个项目初始化文档规范」**

助手会自动完成：

```
确认目标 → 建目录骨架 → 写 AGENTS.md / README / .gitignore
   → 放 6 类文档模板 + prompts 指令 → 装校验脚本
   → git init + pre-commit 钩子 + 安全首次提交（只暂存骨架，防 .env 入库）
   → 跑校验到全 PASS → 汇报 + 一句话纪律清单
```

完整流程定义在 [`skills/project-docs-scaffold/SKILL.md`](skills/project-docs-scaffold/SKILL.md)（第 6 步的首次提交刻意**严禁 `git add -A`**，只暂存骨架路径）。

没有 skill 生态也能用——见下方 [安装](#安装)。

---

## 核心机制

| 机制 | 内容 |
|---|---|
| **一文档一类型**（Diátaxis 分类学） | 文档类型闭集：**五类核心** PRD / DESIGN / ADR / PROGRESS / RETRO + **知识笔记** TECH。目录即类型，文件名即"类型 + 中文语义短语"，禁止跨界混写 |
| **三层记录模型** | 过程层（`docs/_inbox/`，临时产物，不进 git）→ 项目层（`docs/01~05`，"项目发生了什么"）→ 知识层（`docs/06-知识/`，"我学会了什么"，服务复盘与面试） |
| **双读者投影** | 同一份源，两个视图：人读完整叙事（HUMAN 区块），AI 读高熵事实（MUST 区块）+ 文档指针（AGENTS.md）。**禁止维护两份内容** |
| **机器校验闸门** | `validate_docs.py` 检查 8 项：frontmatter / 命名规则 / 必填章节 / 内部链接 / 文档地图登记（双向）/ 知识台账登记 / ADR 编号。可接 pre-commit，违规提交被自动拦截 |
| **知识蒸馏** | 阶段结束用 `prompts/distill.md` 把过程素材蒸馏成正式文档与 TECH 笔记，用判别问题把关（"本轮是否用到此前不了解的技术"），防止笔记泛滥 |
| **契约版本** | 校验器带 `__version__`（`--version` 自查），规则变更记录在 [`CHANGELOG.md`](CHANGELOG.md)。校验器以"复制文件"分发、规则变更不会被存量项目自动感知，因此版本号是唯一的自查手段 |

> **扩展类**：除五类核心与知识笔记外，可按需启用评估台账 `eval-history`、运维手册 `runbook`、测试报告等——加进 `docs-guide.md` 的分类表即可，不破坏核心闭集。

---

## 安装

本技能遵循 **Agent Skills 开放标准**（[agentskills.io](https://agentskills.io/specification)），不绑定任何特定助手。技能目录 `skills/project-docs-scaffold/` 是自包含的——把它整个复制到你的助手能识别的技能目录即可。

### 方式一：装成 skill（推荐）

**通用做法**（适用于支持 `.agents/skills/` 约定的客户端，含 DSH、Codex、Cursor 等）：

```bash
# 用户级：所有项目可用
git clone https://github.com/199Kilig/project-docs-scaffold /tmp/pds
cp -r /tmp/pds/skills/project-docs-scaffold ~/.agents/skills/

# 或项目级：只对当前仓库生效
cp -r /tmp/pds/skills/project-docs-scaffold <你的项目>/.agents/skills/
```

**Claude Code**（`~/.claude/skills/` 或项目内 `.claude/skills/`）：

```bash
cp -r /tmp/pds/skills/project-docs-scaffold ~/.claude/skills/
```

**Hermes** 用户可直接从 GitHub 安装：

```bash
hermes skills install 199Kilig/project-docs-scaffold
```

装好后对助手说一句话即可：

> **「给这个项目初始化文档规范」**

### 方式二：不用 skill，手动复制

核心资产全是普通文件，4 步装配：

1. 复制 `templates/` 下的模板与文档骨架到项目的 `docs/`；
2. 复制 `scripts/validate_docs.py` 到项目的 `scripts/`；
3. 把 `templates/AGENTS.md`（Claude Code 用 `CLAUDE.md`）放到项目根目录，让 AI 遵守文档规范；
4. 按需加 Git pre-commit 钩子（见下方）。

---

## 使用

### 文档纪律

写进 `AGENTS.md`，也是这套体系的全部规则：

1. **一文档一类型**：新建文档前先读 `docs/_templates/` 对应模板，严格按章节填写；内容跨界即拆分，用链接关联；
2. **命名规则**：`类型-<中文语义短语>.md`（如 `PRD-打卡功能.md`、`ADR-004-文档用中文命名.md`）；语义段禁止纯数字/日期；
3. **双读者约定**：MUST 区块（验收标准/接口/约束）是 AI 的事实源；HUMAN 区块（背景/叙事）供人阅读，投喂 AI 时忽略；
4. **过程产物隔离**：临时快照/草稿只进 `docs/_inbox/`（不进 git），阶段结束蒸馏后清空；
5. **登记义务**：每份正式文档必须在 `docs/README.md` 文档地图登记一行；每份 TECH 笔记必须在 `docs/06-知识/README.md` 台账登记一行。
   **反向同样成立**——登记了但文件不存在的"幽灵条目"也是 FAIL。模板里的示例行带 `~` 前缀，不参与校验。

### 校验

```bash
python scripts/validate_docs.py            # 全量校验，PASS/FAIL 输出
python scripts/validate_docs.py docs       # 指定目录
python scripts/validate_docs.py --quiet    # 只回退出码（pre-commit / CI 用）
python scripts/validate_docs.py --version  # 打印校验器契约版本
```

接入 Git pre-commit（零依赖，无需 pre-commit 框架）：

```sh
# .git/hooks/pre-commit
#!/bin/sh
python scripts/validate_docs.py --quiet || { echo "文档校验失败，提交被拦截"; exit 1; }
```

### 蒸馏（阶段收尾）

把 `templates/prompts/distill.md` 交给 AI，它会完成：知识判别 → 素材分类 → 投影草稿 → 成文 → 登记 → 校验 → 清空 inbox。

`templates/prompts/` 下另有三个指令：`write-doc.md`（写新文档）、`feed-agent.md`（把已有文档喂给 AI 时的投喂纪律 + 长文档投影转写）。

---

## 与 AI 编码工具的适配

| 工具 | 文档规范入口 | 说明 |
|---|---|---|
| Claude Code | `CLAUDE.md` | 将 `templates/AGENTS.md` 改写为 `CLAUDE.md` 放入项目根 |
| Codex / Cursor / Copilot | `AGENTS.md` | 原生支持，直接使用模板 |
| 任意工具 + 校验脚本 | `scripts/validate_docs.py` | 不依赖任何工具，提交前手动或钩子运行 |

---

## 目录结构

```
project-docs-scaffold/
├── skills/
│   └── project-docs-scaffold/          # ★ 技能目录（自包含，整目录即安装单元）
│       ├── SKILL.md                    #   技能定义：初始化的 8 步自动流程
│       └── assets/                     #   技能运行所需的全部资产
│           ├── templates/              #     与根 templates/ 同步
│           ├── scripts/validate_docs.py#     与根 scripts/ 同步
│           ├── CHANGELOG.md            #     与根 CHANGELOG.md 同步
│           └── LICENSE
├── PROPOSAL.md               # 设计文档：三层记录模型的推导过程
├── CHANGELOG.md              # 校验器契约的规则变更记录
├── .gitattributes            # *.py 强制 LF（保证跨平台 shebang 可用）
├── docs/                     # 本仓库自身的决策记录（ADR）
├── scripts/
│   ├── validate_docs.py      # 校验闸门（8 项检查，可接 pre-commit，带契约版本号）
│   └── sync_skill_assets.py  # 同步/校验 assets 与根模板、脚本一致（--check 供 CI）
└── templates/                # 工具无关的核心资产
    ├── docs-guide.md         # 项目文档宪法（文档规范唯一来源）
    ├── AGENTS.md             # AI 代理目录（只放指针 + 铁律）
    ├── README.md             # 项目入口骨架
    ├── docs/README.md        # 文档地图骨架（强制登记，双向校验）
    ├── PRD / DESIGN / ADR / PROGRESS / RETRO / TECH 模板
    ├── tech-index.md         # 知识台账骨架（tech-index）
    ├── gitignore             # 完整版（.env 安全红线 / 生成物 / _inbox）
    └── prompts/              # 写作 / 投喂 / 转写 / 蒸馏指令
```

> `skills/…/assets/` 与根目录的 `templates/`、`scripts/validate_docs.py`、`CHANGELOG.md` 内容相同：前者保证技能自包含（Agent Skills 规范要求安装后不依赖仓库其他部分），后者是手动复制路径的来源。改任意一处后跑 `python scripts/sync_skill_assets.py` 保持一致——它同时检查 `SKILL.md` 的 `metadata.version` 是否与 CHANGELOG 最新版本一致，`--check` 可接入 CI。

---

## 设计文档

[`PROPOSAL.md`](PROPOSAL.md) 记录完整设计推导：从"vibe coding 中 agent 用了我并不了解的技术栈"这一痛点出发，论证三层记录模型（过程 / 项目 / 知识）如何服务**复盘回忆**与**面试快查**两个场景。

---

## License

MIT
