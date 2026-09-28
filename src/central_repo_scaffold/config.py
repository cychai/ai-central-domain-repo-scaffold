from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from string import Formatter
from typing import Any
import json, re
import yaml
from jsonschema import Draft202012Validator
from .errors import ConfigError

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")

@dataclass(frozen=True)
class Domain:
    name: str; slug: str; repository: str; description: str; default_branch: str
@dataclass(frozen=True)
class Service:
    id: str; name: str; repository: str; source: str; mount_path: str
    default_branch: str; access: str; fetch_mode: str; verification: tuple[str, ...]
    local_path: str | None = None
@dataclass(frozen=True)
class Worktree:
    root: str; directory_template: str
@dataclass(frozen=True)
class DomainConfig:
    schema_version: int; domain: Domain; services: tuple[Service, ...]; worktree: Worktree
    def public_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "domain": asdict(self.domain),
            "services": [{k:v for k,v in asdict(s).items() if k != "local_path"} for s in self.services],
            "worktree": asdict(self.worktree),
        }

def _root() -> Path: return Path(__file__).resolve().parents[2]
def _fmt_path(parts): return ".".join(str(x) if isinstance(x,str) else f"[{x}]" for x in parts).replace(".[", "[") or "config"
def load_config(path: Path) -> DomainConfig:
    try: raw=yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError,yaml.YAMLError) as exc: raise ConfigError(f"无法读取 YAML：{path}: {exc}") from exc
    schema=json.loads((_root()/"schema/domain.schema.json").read_text(encoding="utf-8"))
    errors=sorted(Draft202012Validator(schema).iter_errors(raw), key=lambda e:list(e.absolute_path))
    if errors:
        err=errors[0]; raise ConfigError(f"{_fmt_path(list(err.absolute_path))}: {err.message}")
    services=tuple(Service(verification=tuple(s["verification"]), **{k:v for k,v in s.items() if k!="verification"}) for s in raw["services"])
    config=DomainConfig(1,Domain(**raw["domain"]),services,Worktree(**raw["worktree"]))
    _validate(config); return config

def _validate(c: DomainConfig):
    for field,value in (("domain.slug",c.domain.slug),("domain.default_branch",c.domain.default_branch)):
        if not SAFE_ID.fullmatch(value) or ".." in value: raise ConfigError(f"{field}: 包含不安全字符")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", c.domain.repository) or ".." in c.domain.repository:
        raise ConfigError("domain.repository: 必须是安全的单级目录名")
    for key in ("id","repository","mount_path"):
        seen={}
        for i,s in enumerate(c.services):
            value=getattr(s,key)
            if value in seen: raise ConfigError(f"services[{i}].{key}: 与 services[{seen[value]}].{key} 重复")
            seen[value]=i
    for i,s in enumerate(c.services):
        if not SAFE_ID.fullmatch(s.id) or "/" in s.id: raise ConfigError(f"services[{i}].id: 包含不安全字符")
        path=PurePosixPath(s.mount_path)
        if path.is_absolute() or len(path.parts)<2 or path.parts[0]!="services" or any(p in (".","..","") for p in path.parts):
            raise ConfigError(f"services[{i}].mount_path: 必须是 services/ 下的安全相对路径")
        for j,cmd in enumerate(s.verification):
            if not cmd.strip() or "\n" in cmd or "\r" in cmd: raise ConfigError(f"services[{i}].verification[{j}]: 必须是单行非空命令")
    fields={n for _,n,_,_ in Formatter().parse(c.worktree.directory_template) if n}
    if fields != {"repository","branch_slug"}: raise ConfigError("worktree.directory_template: 必须且只能包含 {repository} 和 {branch_slug}")
    if "/" in c.worktree.directory_template or "\\" in c.worktree.directory_template:
        raise ConfigError("worktree.directory_template: 必须生成单级目录名，不能包含路径分隔符")
