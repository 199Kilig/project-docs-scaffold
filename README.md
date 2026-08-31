# project-docs-scaffold

面向 vibe coding（AI 辅助开发）的**项目文档治理脚手架**：为任意项目建立"类型化 + 双读者 + 机器校验"的文档体系，让 AI 产出的文档可定位、可校验、可沉淀。

## 背景与问题

Vibe coding 模式下，AI 生成文档速度快但缺乏约束，常见的失控形态：

- **内容混合**：一份文档同时是需求、方案、决策、复盘（"四合一"），定位不明
- **命名随意**：文件名看不出文档讲什么，检索靠猜
- **结构参差**：AI 每次输出的章节结构不一致，质量不可控
- **过程混入成果**：临时快照/草稿与正式文档混放，文档库逐渐变成垃圾场
- **过时无人知**：文档更新与代码演进脱节，无人检查

本脚手架针对这些问题提供一套可执行的治理方案，核心机制全部**工具无关**（Markdown + 一个 Python 校验脚本 + Git hooks），不绑定任何特定 AI 编码工具。

## 核心机制

| 机制 | 内容 |
|---|---|
| **一文档一类型**（Diátaxis 分类学） | 文档类型闭集：PRD / DESIGN / ADR / PROGRESS / RETRO + TECH 知识笔记。目录即类型、文件名即"类型 + 中文语义短语"，禁止跨界混写 |
| **三层记录模型** | 过程层（`docs/_inbox/`，临时产物，不进 git）→ 项目层（`docs/01~05`，项目发生了什么）→ 知识层（`docs/06-知识/`，我学会了什么，服务复盘与面试） |
| **双读者投影** | 同一份源：人类读者读完整叙事（HUMAN 区块），AI 读者读高熵事实（MUST 区块）+ 文档指针（AGENTS.md）。禁止维护两份内容 |
| **机器校验闸门** | `validate_docs.py` 检查：frontmatter / 命名规则 / 必填章节 / 内部链接 / 文档地图登记 / 知识台账登记。可接入 pre-commit 钩子，违规提交被自动拦截 |
| **知识蒸馏** | 阶段结束用 `prompts/distill.md` 把过程素材蒸馏成正式文档与 TECH 笔记，判别问题把关（"本轮是否用到此前不了解的技术"），防止笔记泛滥 |
| **Git 集成** | 自动 `git init`、`.gitignore`（含 .env 安全红线）、pre-commit 钩子、安全首次提交（仅暂存骨架文件） |

## 安装

### 作为 Hermes skill 安装（可选封装层）

本仓库的 `SKILL.md` 是 Hermes 技能格式（skills 生态标准之一），Hermes 用户可一键安装：

```bash
hermes skills install 199Kilig/project-docs-scaffold
```

或手动将 `project-docs-scaffold` 目录放入 Hermes 技能目录（Windows：`C:\Users\<用户>\AppData\Local\hermes\skills\software-development\`；macOS/Linux：`~/.hermes/skills/software-development/`）。

### 用于任意项目（不依赖 Hermes）

核心资产全部是普通文件，直接复制即可：

1. 复制 `templates/` 下的模板与文档骨架到项目的 `docs/`；
2. 复制 `scripts/validate_docs.py` 到项目 `scripts/`；
3. 按需添加 Git pre-commit 钩子（见下文）；
4. 将 `templates/AGENTS.md`（或为 Claude Code 改写为 `CLAUDE.md`）放入项目根目录，让 AI 代理遵守文档规范。

## 使用

### 文档纪律（写入 AGENTS.md 的规则）

1. **一文档一类型**：新建文档前先读 `docs/_templates/` 对应模板，严格按章节填写；内容跨界即拆分，用链接关联；
2. **命名规则**：`类型-<中文语义短语>.md`（如 `PRD-打卡功能.md`、`ADR-004-文档用中文命名.md`）；语义段禁止纯数字/日期；
3. **双读者约定**：MUST 区块（验收标准/接口/约束）为 AI 事实源；HUMAN 区块（背景/叙事）供人阅读，投喂 AI 时忽略；
4. **过程产物隔离**：临时快照/草稿只进 `docs/_inbox/`（不进 git），阶段结束蒸馏后清空；
5. **登记义务**：每份正式文档必须在 `docs/README.md` 文档地图登记一行；每份 TECH 笔记必须在 `docs/06-知识/README.md` 台账登记一行（未登记 = 校验 FAIL）。

### 校验

```bash
python scripts/validate_docs.py          # 全量校验，PASS/FAIL 输出
python scripts/validate_docs.py docs     # 指定目录
```

接入 Git pre-commit（零依赖，无需 pre-commit 框架）：

```sh
# .git/hooks/pre-commit
#!/bin/sh
python scripts/validate_docs.py >/dev/null 2>&1 || { echo "文档校验失败，提交被拦截"; exit 1; }
```

### 蒸馏（阶段收尾）

将 `templates/prompts/distill.md` 作为 prompt 交给 AI，自动完成：知识判别 → 素材分类 → 投影草稿 → 成文 → 登记 → 校验 → 清空 inbox。

## 目录结构

```
project-docs-scaffold/
├── SKILL.md                  # Hermes 技能封装（可选）
├── PROPOSAL.md               # 设计文档：三层记录模型的推导过程
├── scripts/
│   └── validate_docs.py      # 校验闸门（7 项检查，可接 pre-commit）
└── templates/                # 工具无关的核心资产
    ├── docs-guide.md         # 项目文档宪法（文档规范唯一来源）
    ├── AGENTS.md             # AI 代理目录（指针 + 铁律）
    ├── README.md             # 项目入口骨架
    ├── docs/README.md        # 文档地图骨架（强制登记）
    ├── PRD / DESIGN / ADR / PROGRESS / RETRO / TECH 模板
    ├── tech-index.md         # 知识台账骨架
    ├── gitignore             # 完整版（.env / 生成物 / _inbox）
    └── prompts/              # 写作 / 投喂 / 转写 / 蒸馏指令
```

## 与 AI 编码工具的适配

| 工具 | 文档规范入口 | 说明 |
|---|---|---|
| Claude Code | `CLAUDE.md` | 将 `templates/AGENTS.md` 改写为 `CLAUDE.md` 放入项目根 |
| Codex / Cursor / Copilot | `AGENTS.md` | 原生支持，直接使用模板 |
| 任意工具 + 校验脚本 | `scripts/validate_docs.py` | 不依赖工具，提交前手动或钩子运行 |

## 设计文档

[PROPOSAL.md](PROPOSAL.md) 记录完整设计决策：从"vibe coding 中 AI 使用了我不了解的技术栈"这一痛点出发，推导出三层记录模型（过程/项目/知识），并论证知识层如何服务"复盘回忆 + 面试快查"两个场景。

## License

MIT
