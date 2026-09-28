#!/usr/bin/env python3
"""docs 体系校验闸门（validate_docs.py）

用法:
    python scripts/validate_docs.py [docs目录] [--quiet]
    python scripts/validate_docs.py --version

检查项:
    1. frontmatter 必填字段: title / type / status / date / updated
    2. 文件名前缀匹配类型: PRD-<语义> / DESIGN-<语义> / ADR-NNN-<语义> / PROGRESS-日期-<语义> / RETRO-<语义>
       （语义段必须存在且非纯数字/日期）
    3. ADR 编号: 递增且不重复
    4. 必填章节: 按 frontmatter type 对照模板固定章节
    5. 内部链接: 相对链接目标存在
    6. 文档地图登记: 每份正式文档必须在 docs/README.md 地图中有一行
    7. tech-index 登记: 每份 TECH 笔记必须在 docs/06-知识/README.md 台账中有一行
    8. 文档地图反向: 地图/台账中登记的文档必须真实存在（幽灵条目 = FAIL）

退出码: 0=全 PASS, 1=有 FAIL。可接入 pre-commit 或提交前手动跑。

契约版本: __version__。规则每次变更都必须在本文件与 CHANGELOG.md 同步登记，
用户在项目里跑 `--version` 即可自查所处契约版本。
"""
import re
import sys
from pathlib import Path

# ---- 契约版本（与 CHANGELOG.md 同步；规则变更必须同时更新两处）----
__version__ = "1.0.0"

# Windows 控制台默认 GBK，无法编码 ✗ 等符号 → 统一按 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# 读文件统一用 utf-8-sig：带 BOM 的 UTF-8（Windows 记事本 / Set-Content / 部分 AI 工具
# 写出的文件）会让 BOM 留在字符串开头，导致 frontmatter 的 ^--- 匹配失败而误报缺字段。
READ_ENCODING = "utf-8-sig"

# 示例行标记：地图/台账表格中第一列以此开头的行视为示例，正反向校验都跳过。
# 用户改写真实文档后请去掉该标记；不要删除示例行也不会误报。
EXAMPLE_MARK = "~"

# ---- 类型闭集（与 docs-guide.md 分类表保持一致）----
TYPES = {
    "prd":      {"prefix": "PRD-",      "sections": ["## 3. 验收标准", "## 4. 风险清单"]},
    "design":   {"prefix": "DESIGN-",   "sections": ["## 1. 目标与约束", "## 4. 接口定义", "## 5. 非功能需求"]},
    "adr":      {"prefix": "ADR-",      "sections": ["## 背景", "## 决策", "## 被否方案", "## 后果"]},
    "progress": {"prefix": "PROGRESS-", "sections": ["## 已完成"]},
    "retro":    {"prefix": "RETRO-",    "sections": ["## 3. 结果", "## 4. 可复现命令"]},
    "tech":     {"prefix": "TECH-",     "sections": ["## 2. 技术要点（MUST）", "## 3. 操作步骤（MUST）", "## 5. 亮点与代码锚点（MUST）"]},
}
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FM_FIELD_RE = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)
SKIP_DIRS = {"_generated", "_templates", "_inbox", "coverage_html", ".git", "node_modules"}
# 制度文件白名单：不按五类文档检查（docs-guide 宪法、文档地图）
SKIP_FILES = {"docs-guide.md", "README.md"}
LINK_RE = re.compile(r"\]\((\.{1,2}/[^)#\s]+)\)")
HEADER_CELLS = ("文档", "文件", "名称", "文档名", "笔记", "技术")


def read_text(path: Path) -> str:
    """统一读文本：容忍缺失 BOM 与非法字节"""
    return path.read_text(encoding=READ_ENCODING, errors="replace")


def is_docs_type_doc(path: Path) -> bool:
    """只检查已注册类型文档：文件名有类型前缀，或 frontmatter type 在 TYPES 内"""
    name = path.name
    if re.match(r"^(PRD|DESIGN|ADR-\d{3}|PROGRESS-\d{4}-\d{2}-\d{2}|RETRO|TECH)-", name):
        return True
    fm = parse_frontmatter(read_text(path))
    return fm.get("type", "").lower() in TYPES


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text.lstrip("\ufeff"))
    if not m:
        return {}
    return {k: v.strip() for k, v in FM_FIELD_RE.findall(m.group(1))}


def _semantic_tail_ok(tail: str) -> bool:
    """语义段合法：非空、非纯数字、非纯日期（文件名必须能看出内容）"""
    t = tail.strip("-_ ")
    if t.lower().endswith(".md"):
        t = t[:-3].rstrip("-_ ")
    if not t:
        return False
    if t.isdigit():
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return False
    return True


def check_file(path: Path, rel: Path) -> list[str]:
    """返回该文件的问题列表，空列表 = PASS"""
    issues = []
    text = read_text(path)
    fm = parse_frontmatter(text)

    # 1. frontmatter 必填字段
    for field in ("title", "type", "status", "date", "updated"):
        if field not in fm:
            issues.append(f"缺 frontmatter 字段: {field}")

    doc_type = fm.get("type", "").lower()
    if doc_type not in TYPES:
        if fm:
            issues.append(f"type 不在类型闭集内: {doc_type!r}（允许: {', '.join(TYPES)}）")
        return issues

    spec = TYPES[doc_type]
    name = path.name

    # 2. 文件名前缀匹配（类型前缀 + 中文语义段，禁止纯数字/日期作语义）
    if doc_type == "progress":
        m = re.match(r"^PROGRESS-(\d{4}-\d{2}-\d{2})-(.+)$", name)
        ok_prefix = bool(m) and _semantic_tail_ok(m.group(2))
    elif doc_type == "adr":
        m = re.match(r"^ADR-(\d{3})-(.+)$", name)
        ok_prefix = bool(m) and _semantic_tail_ok(m.group(2))
    else:
        m = re.match(rf"^{spec['prefix']}(.+)$", name)
        ok_prefix = bool(m) and _semantic_tail_ok(m.group(1))
    if not ok_prefix:
        issues.append(
            f"文件名不符合命名规则: 应为 {spec['prefix']}<语义短语>.md"
            + "（ADR 用 ADR-NNN-，PROGRESS 用 PROGRESS-日期-；语义段用中文短语，禁止纯数字/日期）"
        )

    # 3. 必填章节
    for sec in spec["sections"]:
        if sec not in text:
            issues.append(f"缺必填章节: {sec}")

    # 4. 内部链接目标存在
    for m in LINK_RE.finditer(text):
        target = m.group(1)
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            issues.append(f"失效链接: {target}")

    return issues


def check_adr_numbering(docs_root: Path) -> list[str]:
    """ADR 编号递增且不重复"""
    issues = []
    adrs = sorted(docs_root.glob("**/ADR-*.md"))
    numbers = []
    for p in adrs:
        m = re.match(r"ADR-(\d+)", p.name)
        if m:
            numbers.append(int(m.group(1)))
    if numbers != sorted(set(numbers)):
        issues.append(f"ADR 编号重复: {numbers}")
    if numbers != sorted(numbers):
        issues.append(f"ADR 编号未递增: {numbers}")
    # 编号应连续从 1 开始（容忍缺失，仅提示）
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        issues.append(f"ADR 编号不连续（缺失编号）: {sorted(numbers)}")
    return issues


def _is_separator(cell: str) -> bool:
    return bool(cell) and set(cell) <= set("-: ")


def _table_rows(table_path: Path) -> list[list[str]] | None:
    """解析 markdown 表格行（返回每行的单元格列表）；文件不存在返回 None"""
    if not table_path.exists():
        return None
    rows = []
    for line in read_text(table_path).splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if cols:
            rows.append(cols)
    return rows


def _table_first_cells(table_path: Path, header_names: tuple[str, ...]) -> list[str] | None:
    """解析 markdown 表格第一列；跳过表头行、分隔行与示例行；文件不存在返回 None"""
    rows = _table_rows(table_path)
    if rows is None:
        return None
    cells = []
    for cols in rows:
        first = cols[0]
        if first in header_names or _is_separator(first):
            continue
        if first.startswith(EXAMPLE_MARK):   # 示例行：不参与登记检查
            continue
        cells.append(first)
    return cells


def check_map_registration(docs_root: Path) -> list[str]:
    """每份正式文档（五类 + tech）必须在 docs/README.md 文档地图中登记一行"""
    cells = _table_first_cells(docs_root / "README.md", ("文档", "文件", "名称", "文档名"))
    if cells is None:
        return ["docs/README.md 文档地图缺失：每份正式文档必须在此登记一行"]

    unregistered = []
    for path in sorted(docs_root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if not is_docs_type_doc(path):
            continue
        # tech 笔记登记到 tech-index 台账（06-知识/README.md），不查 docs 地图
        fm = parse_frontmatter(read_text(path))
        if fm.get("type", "").lower() == "tech":
            continue
        rel = path.relative_to(docs_root).as_posix()
        if not any(path.name in cell or rel in cell for cell in cells):
            unregistered.append(rel)
    if unregistered:
        return [f"未在 docs/README.md 文档地图登记: {', '.join(unregistered)}（每份正式文档一行：文档名/类型/状态/定位）"]
    return []


def check_tech_index_registration(docs_root: Path) -> list[str]:
    """每份 TECH 笔记必须在 docs/06-知识/README.md tech-index 台账登记一行"""
    cells = _table_first_cells(docs_root / "06-知识" / "README.md", ("笔记", "技术", "文档"))
    if cells is None:
        return ["docs/06-知识/README.md tech-index 台账缺失：每份 TECH 笔记必须在此登记一行"]

    unregistered = []
    for path in sorted(docs_root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if not is_docs_type_doc(path):
            continue
        fm = parse_frontmatter(read_text(path))
        if fm.get("type", "").lower() != "tech":
            continue
        rel = path.relative_to(docs_root).as_posix()
        if not any(path.name in cell or rel in cell for cell in cells):
            unregistered.append(rel)
    if unregistered:
        return [f"未在 docs/06-知识/README.md tech-index 台账登记: {', '.join(unregistered)}（每份 TECH 笔记一行：笔记/技术/日期/解决什么问题/亮点/难点）"]
    return []


def _looks_like_doc_ref(cell: str) -> bool:
    """地图/台账的第一列是否是一条文档引用（而非说明文字）"""
    if "/" in cell or "\\" in cell:
        return True
    if cell.endswith(".md"):
        return True
    return False


def _find_in_docs(docs_root: Path, cell: str) -> bool:
    """在 docs 树里定位该引用（先按相对路径，再按文件名兜底，忽略大小写）"""
    rel = cell.replace("\\", "/").lstrip("./")
    if (docs_root / rel).exists():
        return True
    target = Path(rel).name.lower()
    for p in docs_root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name.lower() == target:
            return True
    return False


def check_map_backreference(docs_root: Path) -> list[str]:
    """反向检查：地图/台账里登记的文档必须真实存在（幽灵条目 = FAIL）

    通配符条目（如 docs/02-方案/DESIGN-*.md）与目录说明不作存在性判断。
    """
    issues = []
    checks = [
        ("docs/README.md 文档地图", docs_root / "README.md", ("文档", "文件", "名称", "文档名")),
        ("docs/06-知识/README.md 台账", docs_root / "06-知识" / "README.md", ("笔记", "技术", "文档")),
    ]
    for label, table_path, headers in checks:
        rows = _table_rows(table_path)
        if rows is None:
            continue
        ghosts = []
        for cols in rows:
            cell = cols[0]
            if cell in headers or _is_separator(cell):
                continue
            if cell.startswith(EXAMPLE_MARK):      # 示例行：跳过
                continue
            if "*" in cell or "{{" in cell or "<" in cell:
                continue                            # 通配符/占位符：无法判定存在性
            if not _looks_like_doc_ref(cell):
                continue
            if not _find_in_docs(docs_root, cell):
                ghosts.append(cell)
        if ghosts:
            issues.append(
                f"{label} 登记了不存在的文档（幽灵条目）: {', '.join(ghosts)}"
                "（文档已删除或改名时，请同步删除/更新该登记行）"
            )
    return issues


def main() -> int:
    argv = sys.argv[1:]
    if "--version" in argv or "-V" in argv:
        print(f"validate_docs.py 契约版本 {__version__}")
        return 0

    quiet = "--quiet" in argv
    positional = [a for a in argv if not a.startswith("-")]
    docs_root = Path(positional[0]) if positional else Path("docs")
    if not docs_root.exists():
        if not quiet:
            print(f"FAIL: docs 目录不存在: {docs_root}")
        return 1

    all_issues: list[tuple[str, list[str]]] = []
    for path in sorted(docs_root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if not is_docs_type_doc(path):
            continue  # 扩展类/非五类文档不检查
        rel = path.relative_to(docs_root)
        issues = check_file(path, rel)
        if issues:
            all_issues.append((str(rel), issues))

    adr_issues = check_adr_numbering(docs_root)
    if adr_issues:
        all_issues.append(("(ADR 编号)", adr_issues))

    map_issues = check_map_registration(docs_root)
    if map_issues:
        all_issues.append(("(文档地图)", map_issues))

    tech_issues = check_tech_index_registration(docs_root)
    if tech_issues:
        all_issues.append(("(tech-index)", tech_issues))

    ghost_issues = check_map_backreference(docs_root)
    if ghost_issues:
        all_issues.append(("(地图反向)", ghost_issues))

    if not all_issues:
        if not quiet:
            print(f"PASS: 全部文档合规（契约 v{__version__}）")
        return 0
    if quiet:
        return 1
    print(f"FAIL: {len(all_issues)} 个文件/检查点有问题")
    for name, issues in all_issues:
        print(f"  ✗ {name}")
        for i in issues:
            print(f"      - {i}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
