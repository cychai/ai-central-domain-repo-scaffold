from __future__ import annotations
import os, shutil, tempfile
from pathlib import Path
from .config import load_config
from .generator import expected_files, render_repository, _render_into
from .git import initialize_repository
from .verification import verify_generated_repository
from .errors import GenerationError

def inspect_config(path: Path) -> str:
    c=load_config(path); lines=[f"领域：{c.domain.name}",f"中央仓：{c.domain.repository}",f"服务数量：{len(c.services)}"]
    lines += [f"- {s.id}: {s.access}, {s.fetch_mode}, {s.mount_path}" for s in c.services]
    return "\n".join(lines)
def plan_config(path: Path,output: Path) -> str:
    c=load_config(path); return f"目标：{output}\n默认分支：{c.domain.default_branch}\n文件数量：{len(expected_files())}\n服务数量：{len(c.services)}"
def create_repository(config_path: Path,output: Path,keep_failed=False):
    config=load_config(config_path); output=output.expanduser().resolve()
    if output.exists(): raise GenerationError(f"目标目录已存在，拒绝覆盖：{output}")
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix=f".{output.name}.create-",dir=output.parent))
    try:
        _render_into(config,temp); verify_generated_repository(temp,False)
        sha=initialize_repository(temp,config.domain.default_branch); verify_generated_repository(temp,True)
        os.replace(temp,output); return sha
    except Exception:
        if keep_failed:
            failed=output.parent/f".{output.name}.failed-output"
            if failed.exists(): shutil.rmtree(failed)
            os.replace(temp,failed)
        else: shutil.rmtree(temp,ignore_errors=True)
        raise
