#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from central_repo_scaffold.generator import expected_files

FORBIDDEN = (
    "search_central_incentive_repo",
    "tradeflow-lab",
    "/Users/bytedance",
)
SCAN_PATHS = (
    ROOT / "templates",
    ROOT / "examples",
    ROOT / "src",
    ROOT / "README.md",
    ROOT / "docs",
)


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for candidate in path.rglob("*"):
        if candidate.is_file() and "__pycache__" not in candidate.parts:
            yield candidate


def main() -> int:
    errors: list[str] = []
    for scan_path in SCAN_PATHS:
        for path in iter_files(scan_path):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for forbidden in FORBIDDEN:
                if forbidden in text:
                    errors.append(
                        f"{path.relative_to(ROOT)}: 包含禁止残留 {forbidden!r}"
                    )

    expected_path = ROOT / "examples/expected-tree.txt"
    declared = expected_path.read_text(encoding="utf-8").splitlines()
    actual = list(expected_files())
    if declared != actual:
        errors.append("examples/expected-tree.txt 与模板生成文件集不一致")

    lowercase_agents = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("agent.md")
        if ".venv" not in path.parts
    ]
    if lowercase_agents:
        errors.append(
            "发现非标准小写 Agent 入口：" + ", ".join(map(str, lowercase_agents))
        )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("模板残留、目录合同与 Agent 入口校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
