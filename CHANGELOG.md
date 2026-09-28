# 变更记录（CHANGELOG）

本文件记录 **validator 契约**（`scripts/validate_docs.py`）的规则变更。

## 为什么需要这份文件

校验器是用「复制文件到项目」的方式分发的——不是依赖安装，没有版本约束。因此规则一旦变更，**存量项目不会自动感知**：要么一直用旧规则，要么换了新脚本后突然出现一批新的 FAIL。

所以规则每次变更都必须在两处同步登记：

1. `scripts/validate_docs.py` 顶部的 `__version__`
2. 本文件

用户在自己项目里跑下面这条命令即可自查所处契约版本：

```bash
python scripts/validate_docs.py --version
```

## 变更类型说明

| 类型 | 含义 |
|---|---|
| `Breaking` | 存量项目升级后会**新增 FAIL**，需要按"升级动作"处理 |
| `Fixed` | 修掉误报或错误行为；升级后 FAIL **可能减少**（之前被误报掩盖的真问题会浮现） |
| `Added` | 新增检查项 |
| `Changed` | 行为调整，不改变判定结果 |

---

## [Unreleased]

### Changed

- **技能改为 Agent Skills 标准结构**（校验规则未变，故不影响 validator 契约版本）
  - `SKILL.md` 移入 `skills/project-docs-scaffold/`，`name` 与父目录名一致；仓库根不再放 `SKILL.md`
  - frontmatter 收敛为规范字段：必需的 `name` / `description`，可选 `license` / `compatibility` / `metadata`（扁平字符串映射）
  - 移除 Hermes 专有字段 `version` / `author` / `platforms` / `metadata.hermes`（`author` 改为仓库所有者）
  - `description` 改写为"能力 + 触发场景"完整句式，提高各客户端的技能召回准确度
  - 技能目录自包含：模板与校验脚本以 `assets/` 副本随技能分发
  - 新增 `scripts/sync_skill_assets.py`：同步/校验 `assets/` 与根 `templates/`、`scripts/` 一致（`--check` 供 CI）
  - 决策记录见 `docs/03-决策/ADR-001-技能采用AgentSkills标准结构.md`
  - **升级动作**：已安装旧版技能（根目录 `SKILL.md`）的副本需替换为新技能目录

### 未变更

- 校验器的 8 项检查逻辑与契约版本 `1.0.0` 均未变动；本次改造只涉及技能封装形态。

---

## [1.0.0] — 2026-09-01

契约首次显式版本化。此前 `validate_docs.py` 的规则集视为 `0.9.0`（未版本化，无变更记录）。

### Fixed

- **BOM 导致 frontmatter 全量误报**：读文件改用 `utf-8-sig`。此前带 BOM 的 UTF-8 文件（Windows 记事本、PowerShell `Set-Content -Encoding UTF8`、部分 AI 工具写出的文件）会让 BOM 留在字符串开头，`^---` 匹配失败，进而误报「缺 frontmatter 字段: title/type/status/date/updated」。
  - ⚠️ **注意**：升级后这类文件的误报会消失，**其真实问题会浮现**（例如字段确实缺失）。如果之前一直 PASS，升级后变 FAIL，属于误报被修掉后的正常结果。
- `--quiet` 之前只被读取、从未生效，且 `--quiet` 写在位置参数前会被当成目录名（报「docs 目录不存在: --quiet」）。现在真正生效，且参数顺序无关。
- `--version` / `-V` 新增，输出契约版本且不执行校验。

### Added

- **文档地图反向校验**：`docs/README.md` 地图与 `docs/06-知识/README.md` 台账中登记的文档必须真实存在，否则 FAIL。此前只做单向检查（新文档未登记会 FAIL，但文档删除后残留的登记行永远查不出来）。
- **示例行约定**：地图/台账表格第一列以 `~` 开头的行视为示例行，正向（登记检查）与反向（存在性检查）都跳过。模板中的示例行已全部加上该前缀。
  - 把示例改写成真实文档时，去掉 `~` 前缀即可纳入校验。
  - 通配符条目（如 `docs/02-方案/DESIGN-*.md`）与占位符（含 `{{`／`<`）不作存在性判断。

### Breaking

- **文档地图/台账中的幽灵条目**：升级后，登记了但文件不存在的行会 FAIL。
  - 升级动作：删除该登记行；若暂时想保留模板示例，给第一列加 `~` 前缀。

### 未变更

- 检查项 1~7（frontmatter 必填字段、命名规则、ADR 编号、必填章节、内部链接、地图登记、tech-index 登记）的判定逻辑与 `0.9.0` 一致。
- 已知待办（尚未纳入本版本）：`status` 取值枚举校验、`date`/`updated` 格式校验、ADR「已取代」指向新 ADR、ADR 编号不连续降级为 WARN、TECH 台账条件校验（无 TECH 笔记时不查台账）。
