---
title: ADR-001：技能采用 Agent Skills 标准结构
type: adr
status: 已接受
date: 2026-09-01
updated: 2026-09-01
links: [../../skills/project-docs-scaffold/SKILL.md]
---
# ADR-001：技能采用 Agent Skills 标准结构

> 类型：adr
> 状态：已接受
> 读者：想知道"为什么改 SKILL.md 的位置和字段"的人（含 AI）
> 结论：把 `SKILL.md` 从仓库根移入 `skills/project-docs-scaffold/` 并只保留规范字段，使其能被任意支持 Agent Skills 的工具加载，不再依赖 Hermes。

## 背景

改造前，`SKILL.md` 位于仓库根目录，frontmatter 为：

```yaml
name: project-docs-scaffold
description: Use when 初始化项目文档体系/搭 docs 骨架。…
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docs, documentation, scaffolding, diataxis, agents-md, docs-as-code]
    related_skills: [speckit-constitution, web-research]
```

两个具体问题：

1. **位置不符合 Agent Skills 规范**。规范要求技能是一个目录且其中含 `SKILL.md`，并且 `name` 必须与父目录名一致。仓库根的父目录名取决于用户克隆时的目录名，不保证等于 `project-docs-scaffold`；同时 `SKILL.md` 与 `README.md` 等开发文件平级混放，无法作为独立单元安装。
2. **字段超出规范**。`version` / `author` / `platforms` 是规范外字段；`metadata` 规范要求是 `string → string` 扁平映射，而 `metadata.hermes.tags` 是嵌套数组。

当时 README 的定位是"Hermes 技能格式（skills 生态标准之一）"，`author` 甚至写作 `Hermes Agent`，对外读起来像是有生态绑定。

## 决策

采用 **Agent Skills 开放标准**（`agentskills.io`，被 Claude Code / Codex / Cursor 等实现）作为唯一目标格式：

1. 技能移入标准目录 `skills/project-docs-scaffold/`，`name` 与目录名一致；仓库根不再放 `SKILL.md`（避免同一技能被重复发现）。
2. frontmatter 收敛为规范字段：必需的 `name` / `description`，可选 `license` / `compatibility` / `metadata`（扁平字符串映射）。Hermes 专有字段全部移除，`author` 改为仓库所有者。
3. `description` 改写为"能力 + 触发场景"的完整句式，并在正文首段复述触发语——各实现主要靠 `description` 做技能召回。
4. 技能目录自包含：模板与校验脚本以 `assets/` 副本随技能分发（规范要求安装后不依赖仓库其他部分）。
5. 新增 `scripts/sync_skill_assets.py` 保证根目录与 `assets/` 两份内容不漂移（`--check` 供 CI / pre-commit 用）。

## 被否方案

| 方案 | 否掉原因 |
|---|---|
| 保留根目录 `SKILL.md`，只精简 frontmatter | 仍不满足"技能 = 独立目录"与"name 匹配父目录名"，无法作为单元安装；且根目录混放开发文件 |
| 为每个工具各维护一份技能文件（Hermes / Claude / Cursor 各一份） | 同一份流程维护 N 份必然漂移；而 Agent Skills 已是共同标准，重复无收益 |
| 技能目录内用软链指向根目录模板 | Windows 下 Git 克隆软链需开发者模式或管理员权限，普通用户会拿到不可用副本 |
| 整体仓库即技能目录（把开发文件移入 `dev/`） | 改动面大于收益，且会让"复制脚手架"的既有用法与技能安装产生语义冲突 |

## 后果

正面：

- 技能可被任意支持 Agent Skills 的工具加载；除 `~/.agents/skills/` 等通用约定外，各工具的技能目录多为复制整个技能目录即可，安装不再依赖某个生态的包管理器。
- `description` 与正文触发语面向所有工具，召回不依赖 Hermes。
- 资产一致性有脚本兜底，`assets/` 副本不会静默过期。

负面 / 代价：

- **模板与校验脚本存在两份**（仓库根 + `assets/`）。改模板或改校验器时必须跑 `sync_skill_assets.py`，否则两份漂移。这是规范"技能自包含"带来的必然成本。
- 仓库根不再有 `SKILL.md`，原先按根路径引用的外部链接或已安装副本需要重新指向 `skills/project-docs-scaffold/`。
- `metadata.version` 与 git tag / CHANGELOG 是三处独立维护的版本信息，需要人工保持一致。

---

*编号递增不重用；被取代时保留本文件，状态改"已取代"，指向新 ADR。*
