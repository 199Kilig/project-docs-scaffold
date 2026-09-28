#!/usr/bin/env python3
"""同步/校验技能资产与仓库根的模板、脚本

背景：技能目录 `skills/project-docs-scaffold/assets/` 必须是自包含的
（Agent Skills 规范要求技能安装后不依赖仓库其他部分），因此模板与校验脚本
在两处各有一份。本脚本保证两份不漂移。

用法:
    python scripts/sync_skill_assets.py           # 把根目录的内容同步进技能目录
    python scripts/sync_skill_assets.py --check   # 只检查是否一致（CI / pre-commit 用）

退出码: 0=一致或同步成功, 1=不一致(--check) 或出错
"""
import filecmp
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parent.parent
SKILL_ASSETS = REPO / "skills" / "project-docs-scaffold" / "assets"

# (根目录来源, 技能目录目标)
PAIRS = [
    (REPO / "templates", SKILL_ASSETS / "templates"),
    (REPO / "scripts" / "validate_docs.py", SKILL_ASSETS / "scripts" / "validate_docs.py"),
    (REPO / "LICENSE", SKILL_ASSETS / "LICENSE"),
]
# 根目录 scripts/ 下不进入技能的开发用脚本
SKIP_NAMES = {"sync_skill_assets.py", "__pycache__"}


def rel_files(root: Path) -> set[str]:
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not any(part in SKIP_NAMES for part in p.parts)
    }


def compare(src: Path, dst: Path) -> list[str]:
    """返回不一致项描述；完全一致返回空列表"""
    problems = []
    if src.is_file():
        if not dst.exists():
            return [f"缺失: {dst.relative_to(REPO)}"]
        if not filecmp.cmp(src, dst, shallow=False):
            problems.append(f"内容不同: {dst.relative_to(REPO)}")
        return problems

    if not dst.exists():
        return [f"缺失目录: {dst.relative_to(REPO)}"]

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


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    drift: list[str] = []

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

    if check_only:
        if drift:
            print("FAIL: 技能资产与仓库根不一致，请跑 python scripts/sync_skill_assets.py")
            for p in drift:
                print(f"  ✗ {p}")
            return 1
        print("PASS: 技能资产与仓库根一致")
        return 0

    if not drift:
        print("PASS: 技能资产与仓库根已一致，无需同步")
    else:
        print(f"已同步 {len(drift)} 处差异")
    return 0


if __name__ == "__main__":
    sys.exit(main())
