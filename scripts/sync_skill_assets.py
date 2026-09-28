#!/usr/bin/env python3
"""同步/校验技能资产，并检查版本一致性

背景：技能目录 `skills/project-docs-scaffold/assets/` 必须是自包含的
（Agent Skills 规范要求技能安装后不依赖仓库其他部分），因此模板、校验脚本、
CHANGELOG 在两处各有一份。本脚本保证两份不漂移，并检查版本号是否自洽。

用法:
    python scripts/sync_skill_assets.py           # 把根目录的内容同步进技能目录
    python scripts/sync_skill_assets.py --check   # 只检查（CI / pre-commit 用）

检查项:
    1. assets/ 与根 templates/、scripts/、CHANGELOG.md 内容一致
    2. SKILL.md 的 metadata.version 与 CHANGELOG 最新版本号一致

退出码: 0=一致, 1=有差异(--check) 或出错
"""
import filecmp
import re
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO / "skills" / "project-docs-scaffold"
SKILL_MD = SKILL_DIR / "SKILL.md"
SKILL_ASSETS = SKILL_DIR / "assets"
CHANGELOG = REPO / "CHANGELOG.md"

# (根目录来源, 技能目录目标)
PAIRS = [
    (REPO / "templates", SKILL_ASSETS / "templates"),
    (REPO / "scripts" / "validate_docs.py", SKILL_ASSETS / "scripts" / "validate_docs.py"),
    (REPO / "LICENSE", SKILL_ASSETS / "LICENSE"),
    (CHANGELOG, SKILL_ASSETS / "CHANGELOG.md"),
]
# 根目录 scripts/ 下不进入技能的开发用脚本
SKIP_NAMES = {"sync_skill_assets.py", "__pycache__"}


def rel_files(root: Path) -> set:
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not any(part in SKIP_NAMES for part in p.parts)
    }


def compare(src: Path, dst: Path) -> list:
    """返回不一致项描述；完全一致返回空列表"""
    problems = []
    if src.is_file():
        if not dst.exists():
            return [f"缺失: {dst.relative_to(REPO)}"]
        if not filecmp.cmp(src, dst, shallow=False):
            problems.append(f"内容不同: {dst.relative_to(REPO).as_posix()}")
        return problems

    if not dst.exists():
        return [f"缺失目录: {dst.relative_to(REPO).as_posix()}"]

    s, d = rel_files(src), rel_files(dst)
    for name in sorted(s - d):
        problems.append(f"技能目录缺少: {name}")
    for name in sorted(d - s):
        problems.append(f"技能目录多出: {name}")
    for name in sorted(s & d):
        if not filecmp.cmp(src / name, dst / name, shallow=False):
            problems.append(f"内容不同: {name}")
    return problems


def sync(src: Path, dst: Path) -> None:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def skill_version() -> str | None:
    """从 SKILL.md 的 frontmatter 读 metadata.version"""
    if not SKILL_MD.exists():
        return None
    text = SKILL_MD.read_text(encoding="utf-8-sig")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    vm = re.search(r"(?m)^\s+version:\s*[\"']?([\w.\-]+)[\"']?\s*$", m.group(1))
    return vm.group(1) if vm else None


def changelog_version() -> str | None:
    """CHANGELOG 中最新的已发布版本号（跳过 [Unreleased]）"""
    if not CHANGELOG.exists():
        return None
    for m in re.finditer(r"(?m)^##\s*\[([^\]]+)\]", CHANGELOG.read_text(encoding="utf-8-sig")):
        v = m.group(1).strip()
        if v.lower() != "unreleased":
            return v
    return None


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    drift: list = []

    # 1. 内容一致性
    for src, dst in PAIRS:
        if not src.exists():
            print(f"FAIL: 来源不存在: {src.relative_to(REPO)}")
            return 1
        problems = compare(src, dst)
        if problems:
            drift.extend(problems)
            if not check_only:
                sync(src, dst)
                print(f"已同步: {src.relative_to(REPO)} → {dst.relative_to(REPO)}")

    # 2. 版本一致性
    sv, cv = skill_version(), changelog_version()
    version_problems = []
    if sv is None:
        version_problems.append("SKILL.md 未找到 metadata.version")
    if cv is None:
        version_problems.append("CHANGELOG 未找到已发布版本号")
    elif sv is not None and sv != cv:
        version_problems.append(
            f"版本不一致: SKILL.md metadata.version={sv} 但 CHANGELOG 最新版本={cv}"
        )

    if check_only:
        ok = True
        if drift:
            ok = False
            print("FAIL: 技能资产与仓库根不一致，请跑 python scripts/sync_skill_assets.py")
            for p in drift:
                print(f"  ✗ {p}")
        if version_problems:
            ok = False
            print("FAIL: 版本号不自洽")
            for p in version_problems:
                print(f"  ✗ {p}")
        if ok:
            print(f"PASS: 技能资产一致，版本自洽（技能 v{sv}）")
            return 0
        return 1

    if drift:
        print(f"已同步 {len(drift)} 处差异")
    for p in version_problems:
        print(f"WARN: {p}")
    if not drift and not version_problems:
        print(f"PASS: 技能资产与仓库根已一致，版本自洽（技能 v{sv}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
