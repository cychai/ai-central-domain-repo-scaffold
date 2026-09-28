from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess, sys
from .errors import VerificationError
from .generator import expected_files
@dataclass(frozen=True)
class VerificationReport:
    passed: bool; checks: tuple[str,...]
def verify_generated_repository(path: Path, require_git: bool=False) -> VerificationReport:
    root=path.resolve(); missing=[p for p in expected_files() if not (root/p).exists()]
    if missing: raise VerificationError("缺少生成文件："+", ".join(missing))
    checks=["structure"]
    if require_git:
        result=subprocess.run(["git","-C",str(root),"rev-parse","--verify","HEAD"],text=True,capture_output=True)
        if result.returncode: raise VerificationError("生成仓缺少 committed HEAD")
        checks.append("git-head")
    result=subprocess.run([sys.executable,"scripts/verify-central.py"] + (["--require-git"] if require_git else []),cwd=root,text=True,capture_output=True)
    if result.returncode: raise VerificationError(result.stderr.strip() or result.stdout.strip() or "生成仓验证失败")
    checks.append("generated-verifier"); return VerificationReport(True,tuple(checks))
