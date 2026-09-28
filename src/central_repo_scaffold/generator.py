from __future__ import annotations
import json, os, shutil, tempfile
from pathlib import Path, PurePosixPath
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError
from .config import DomainConfig
from .errors import GenerationError
from .records import build_record_context

_SPECIAL={"gitignore.j2":".gitignore","dev-worktree.env.example.j2":".dev-worktree.env.example","services/gitkeep.j2":"services/.gitkeep"}
def _root(): return Path(__file__).resolve().parents[2]
def _template_root(): return _root()/"templates"
def _destination(relative: str) -> str:
    if relative in _SPECIAL: return _SPECIAL[relative]
    return relative[:-3] if relative.endswith(".j2") else relative
def expected_files() -> tuple[str,...]:
    files=[_destination(str(p.relative_to(_template_root()))) for p in _template_root().rglob("*.j2")]
    files.append("domain.yaml")
    return tuple(sorted(files))
def render_repository(config: DomainConfig, output: Path) -> list[str]:
    output=output.expanduser().resolve()
    if output.exists(): raise GenerationError(f"目标目录已存在，拒绝覆盖：{output}")
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix=f".{output.name}.render-",dir=output.parent))
    try:
        _render_into(config,temp)
        os.replace(temp,output)
    except Exception:
        shutil.rmtree(temp,ignore_errors=True)
        raise
    return list(expected_files())
def _render_into(config: DomainConfig, root: Path):
    env=Environment(loader=FileSystemLoader(_template_root()),undefined=StrictUndefined,autoescape=False,keep_trailing_newline=True,trim_blocks=True,lstrip_blocks=True)
    context=build_record_context(config,expected_files())
    try:
        for source in sorted(str(p.relative_to(_template_root())) for p in _template_root().rglob("*.j2")):
            dest=root/_destination(source); dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(env.get_template(source).render(**context),encoding="utf-8")
    except TemplateError as exc: raise GenerationError(f"模板渲染失败：{exc}") from exc
    public=config.public_dict()
    public["services"]=[{**s,"verification":list(s["verification"])} for s in public["services"]]
    # JSON is valid YAML 1.2 and lets generated repositories stay dependency-free.
    (root/"domain.yaml").write_text(
        json.dumps(public, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for script in (root/"scripts/dev-worktree.py",root/"scripts/verify-central.py"):
        script.chmod(0o755)
