from __future__ import annotations
from pathlib import Path
import subprocess
from .errors import GitError

def _run(root: Path,*args: str,check=True):
    result=subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True)
    if check and result.returncode: raise GitError(f"Git 命令失败（git {' '.join(args)}）：{result.stderr.strip()}")
    return result
def initialize_repository(path: Path,branch: str) -> str:
    if (path/".git").exists(): raise GitError(f"目标已经是 Git 仓库：{path}")
    for key,label in (("user.name","姓名"),("user.email","邮箱")):
        result=_run(path,"config","--get",key,check=False)
        if result.returncode or not result.stdout.strip(): raise GitError(f"缺少 Git 身份{label}；请先配置 user.name 和 user.email")
    _run(path,"init","-b",branch)
    report=path/"docs/build-record/08-verification-report.md"
    if report.exists(): report.write_text(report.read_text(encoding="utf-8").replace("| Git 初始化与首个提交 | `not-executed` | `render` 阶段不执行；由 `git-init` 或 `create` 完成 |","| Git 初始化与首个提交 | `passed` | 本仓当前首个提交包含全部生成文件 |"),encoding="utf-8")
    _run(path,"add","."); _run(path,"commit","-m","chore: initialize central domain repository")
    return _run(path,"rev-parse","HEAD").stdout.strip()
