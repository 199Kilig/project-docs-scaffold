---
name: project-docs-scaffold
description: Use when 初始化项目文档体系/搭 docs 骨架。生成 AGENTS.md+文档模板（核心五类+知识笔记）+校验脚本。
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docs, documentation, scaffolding, diataxis, agents-md, docs-as-code]
    related_skills: [speckit-constitution, web-research]
---

# 项目文档体系脚手架（project-docs-scaffold）

Use when 用户说"给这个项目初始化文档规范 / 搭 docs 骨架 / 文档太乱帮我规范 / 新建项目要文档体系"。

## 核心模型（四句话）

1. **一文档一类型**（Diátaxis 内核）：文档类型 = 核心五类（PRD/DESIGN/ADR/PROGRESS/RETRO）+ 扩展类（tech 等），目录即类型，文件名即类型+中文语义短语，禁止跨界混写。
2. **双读者投影**：同一份源，人读完整叙事版（HUMAN 区块），AI 读 AGENTS.md 指针 + MUST 区块；禁止维护两份内容。
3. **产物管道**：agent 临时产物（快照/草稿/中间输出）只进 `docs/_inbox/`（不进 git），阶段结束时蒸馏成类型文档、登记地图、清空 inbox；禁止把过程堆进正式文档。
4. **校验闸门**：frontmatter/命名（含语义段）/必填章节/链接/文档地图登记由 `validate_docs.py` 机器检查，AI 产出不合格 = 打回重写。

## 生成步骤（执行顺序）

1. **确认目标**：项目根目录（默认当前工作目录或用户指定）。若已存在 `docs/docs-guide.md` → 告诉用户体系已存在，询问是否升级/跳过，**禁止覆盖已有 docs-guide**。
2. **生成目录骨架**（不存在的才建）：
   ```
   docs/
   ├── README.md            ← 文档地图（强制登记，未登记 = 校验 FAIL）
   ├── docs-guide.md        ← 文档宪法（从 templates/ 复制，可改）
   ├── 01-需求/ 02-方案/ 03-决策/ 04-进度/ 05-复盘/
   ├── 06-知识/             ← 知识层：TECH 笔记 + tech-index 台账（面试/复盘快查）
   ├── _templates/  _generated/  _inbox/
   ```
   `_inbox/` 是过程产物暂存区（agent 快照/草稿），gitignore 掉、不进 git。
3. **写根文件**：`AGENTS.md`（若已有则合并文档规范节，不覆盖其他内容）、README.md 骨架（若 README 已有内容则只在底部加文档地图链接节，不重写）、`.gitignore` 追加 `docs/_generated/` 与 `docs/_inbox/`。
4. **写模板**：把 templates/ 下 6 个文档模板（五类 + TECH）+ prompts 说明（含 distill 蒸馏指令）复制到 `docs/_templates/`。
5. **写校验脚本**：`scripts/validate_docs.py` 复制到项目（路径：项目根 `scripts/validate_docs.py`，或用户指定）。
6. **git 初始化**（安全降级，细则见下）：
   - 检测：`git rev-parse --is-inside-work-tree` → 已有 git 上下文（本目录或父目录）则**跳过整步**并告知用户
   - 无仓库 → `git init`
   - 写 `.gitignore`（若项目还没有）：用 templates/gitignore 完整版
   - 写 `.git/hooks/pre-commit`（若还没有）：内容为"跑 `python scripts/validate_docs.py`，非 0 则阻止提交"——零依赖钩子，不装 pre-commit 框架
   - 首次提交：**只 add 骨架路径**（AGENTS.md README.md docs/ scripts/ .gitignore），**严禁 `git add -A` / `git add .`**（防 .env 等敏感文件入库）；提交信息 `docs: 初始化文档体系脚手架`。pre-commit 钩子会在提交时自动跑校验，FAIL 则提交被拦
   - 安全降级：git 未配置 user.name/email → 只 init 不 commit，提示用户配置后自行提交；git 不可用/命令失败 → 跳过整步，**不影响文档生成**
7. **验证**：跑 `python scripts/validate_docs.py`，必须全 PASS；有 FAIL 就地修复后重跑。
8. **汇报**：初始化报告（建了什么/校验 PASS/git 状态/文档地图入口）+ 一句话纪律清单（见下）。**同时提醒用户：删除 docs/README.md 地图与 docs/06-知识/README.md 台账里的示例行**（示例文档并不存在，留着会误导）。

## 生成后必须告诉用户的纪律清单

- 新建文档：先读 `docs/_templates/` 对应模板，严格按章节填；一份文档只能是一个类型，跨界就拆；文件名用 `类型-<中文语义短语>.md`（如 `PRD-打卡功能.md`），写完在 `docs/README.md` 地图登记一行。
- 给 AI 喂文档：固定指令"只提取元信息头块 + MUST 区块，忽略 HUMAN 区块"，或让 AI 先做 20 行投影转写。
- agent 的临时快照/草稿：只放 `docs/_inbox/`，禁止写进正式文档；阶段结束用 distill 指令蒸馏成类型文档后清空。
- 新技术沉淀：阶段结束蒸馏时，用判别问题"本轮有没有用到此前不了解的技术"把关；有则写 `TECH-<技术>-<语义>.md` 笔记并在 `docs/06-知识/README.md` 台账登记一行（面试前只扫这张表）。
- ADR 编号递增不重用，被取代的保留原文件改状态为"已取代"并指向新 ADR。

## 文件清单与来源

| 目标文件 | 来源 |
|---|---|
| docs/docs-guide.md | templates/docs-guide.md（项目文档宪法，可裁剪） |
| AGENTS.md | templates/AGENTS.md（合并进已有文件） |
| README.md 骨架 | templates/README.md（已有 README 则只加链接节） |
| docs/README.md | templates/docs/README.md（文档地图） |
| docs/_templates/PRD-模板.md | templates/PRD-template.md |
| docs/_templates/DESIGN-模板.md | templates/DESIGN-template.md |
| docs/_templates/ADR-模板.md | templates/ADR-template.md |
| docs/_templates/PROGRESS-模板.md | templates/PROGRESS-template.md |
| docs/_templates/RETRO-模板.md | templates/RETRO-template.md |
| docs/_templates/TECH-模板.md | templates/TECH-template.md（知识笔记：我学会了什么，服务复盘/面试） |
| docs/06-知识/README.md（tech-index 台账） | templates/tech-index.md（面试快查表，强制登记） |
| scripts/validate_docs.py | scripts/validate_docs.py |
| .gitignore | templates/gitignore（完整版：.env/生成物/Python/Node/IDE） |
| docs/_templates/prompts/（写作/投喂/转写/蒸馏指令） | templates/prompts/ |
| docs/_inbox/（过程产物暂存区，gitignore） | 空目录，git 不跟踪 |

## 校验脚本能力（validate_docs.py）

- 扫描 docs/**/*.md（跳过 _generated/、_inbox/、_templates/、coverage 产物）
- frontmatter 必填字段：title/type/status/date/updated（缺 = FAIL）
- 文件名匹配命名规则：`类型-<语义短语>`（PRD-/DESIGN-/ADR-数字-/PROGRESS-日期-/RETRO-；语义段禁止纯数字/日期）
- ADR 编号：递增且不重复
- 必填章节：每类型模板的固定章节标题必须存在（用 frontmatter type 对应检查）
- 内部链接：`](./xxx` 相对链接目标存在
- 文档地图登记：每份正式文档必须在 docs/README.md 地图有一行（未登记 = FAIL）
- tech-index 登记：每份 TECH 笔记必须在 docs/06-知识/README.md 台账有一行（未登记 = FAIL）
- 输出：PASS/FAIL 汇总 + 每文件问题行

## Pitfalls

- **别覆盖**：已有 docs-guide/AGENTS.md 时先问，禁止无脑重写。
- **别生成生成物**：coverage_html、*.html 报告放 docs/_generated/，不进 git（.gitignore 已含）。
- **别把模板当正文**：模板文件带 `{{项目名}}` 占位符，生成时替换为真实项目名。
- **类型封顶**：核心闭集 = 五类（PRD/DESIGN/ADR/PROGRESS/RETRO）+ 知识类（tech，默认启用，目录 06-知识/）。用户想再加类型（eval-history/runbook 等）→ 走"扩展类"，加在 docs-guide 分类表，不破坏核心闭集。

## Verification

- `python scripts/validate_docs.py` 全 PASS
- docs/ 五类目录存在且非空（至少含模板）；06-知识/ 存在且含 tech-index 台账
- docs/_inbox/ 存在且被 gitignore
- AGENTS.md 含"文档地图"节和"铁律"节（铁律含语义段命名/地图登记/inbox）
- .gitignore 含 docs/_generated/ 与 docs/_inbox/
