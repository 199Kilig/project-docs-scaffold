# project-docs-scaffold

> 一句话：**给 AI 协作项目一键生成文档治理体系** —— AGENTS.md + 六类文档模板（五类 + 知识笔记）+ 校验闸门 + git 集成。

Vibe coding（AI 辅助开发）最大的隐性成本不是代码，是**文档失控**：AI 写的文档内容混合、命名随意、结构参差，人看不懂，AI 自己下次也找不到。这个 skill 把文档体系变成一条命令的事。

## 核心特性

| 机制 | 解决什么 |
|---|---|
| **一文档一类型**（Diátaxis 内核） | 六类闭集：PRD / DESIGN / ADR / PROGRESS / RETRO + TECH 知识笔记。目录即类型、文件名即类型+中文语义，禁止跨界混写 |
| **三层记录模型** | 过程层（`_inbox/`，用完即弃）→ 项目层（01~05，项目发生了什么）→ 知识层（06-知识/，我学会了什么，面试弹药库） |
| **双读者投影** | 同一份源：人读完整叙事（HUMAN 区块），AI 读指针 + 高熵事实（MUST 区块）。禁止维护两份内容 |
| **校验闸门** | `validate_docs.py` 机器检查：frontmatter / 命名规则 / 必填章节 / 链接 / 文档地图登记 / tech-index 登记。AI 产出不合格 = 打回重写，pre-commit 自动拦截 |
| **知识蒸馏** | 阶段结束用 distill 指令把过程素材蒸馏成正式文档 + TECH 笔记，判别问题把关，防止笔记泛滥 |
| **git 集成** | 自动 `git init` + .gitignore + pre-commit 钩子 + 安全首次提交（只 add 骨架，绝不含 .env） |

## 安装

### 方式一：GitHub 直接安装（推荐）

```bash
hermes skills install 199Kilig/project-docs-scaffold
```

### 方式二：手动

下载本仓库，把 `project-docs-scaffold` 整个文件夹放到你的 Hermes 技能目录：

- **Windows**：`C:\Users\<用户名>\AppData\Local\hermes\skills\software-development\`
- **macOS / Linux**：`~/.hermes/skills/software-development/`

## 使用

对任意项目说一句：

> **"给这个项目初始化文档规范"**

Hermes 会自动完成 8 步：确认目标 → 建目录骨架（01~06 + _inbox）→ 写 AGENTS.md / README / .gitignore → 放 6 个文档模板 + prompts 指令 → 装校验脚本 → git 初始化 + pre-commit 钩子 + 首次提交 → 全量校验 PASS → 输出初始化报告。

之后写文档的三条纪律（skill 会提示）：

1. **一文档一类型**：先读 `docs/_templates/` 对应模板，跨界就拆，用链接关联；
2. **给 AI 喂文档**："只提取元信息头块 + MUST 区块，忽略 HUMAN 区块"；
3. **过程产物只进 `_inbox/`**：阶段结束用 distill 指令蒸馏成正式文档后清空。

## 目录结构

```
project-docs-scaffold/
├── SKILL.md                  ← skill 主文件（8 步生成流程）
├── PROPOSAL.md               ← 设计文档：三层记录模型（为什么这么设计）
├── scripts/
│   └── validate_docs.py      ← 校验闸门（7 项检查，可接 pre-commit）
└── templates/
    ├── docs-guide.md         ← 项目文档宪法（写任何文档前先读）
    ├── AGENTS.md             ← 给 AI 的项目目录（指针 + 铁律）
    ├── README.md / docs/README.md  ← 项目入口 + 文档地图骨架
    ├── PRD / DESIGN / ADR / PROGRESS / RETRO / TECH 模板
    ├── tech-index.md         ← 知识台账骨架（面试快查表）
    ├── gitignore             ← 完整版（.env / 生成物 / _inbox / Python / Node）
    └── prompts/              ← 写作 / 投喂 / 转写 / 蒸馏指令
```

## 设计文档

[PROPOSAL.md](PROPOSAL.md) 记录了完整的决策过程：从"vibe coding 中 agent 用了我不了解的技术栈"这一原始痛点出发，推导出三层记录模型（过程层 / 项目层 / 知识层），以及知识层如何服务"复盘回忆 + 面试快查"两个场景。

## License

MIT
