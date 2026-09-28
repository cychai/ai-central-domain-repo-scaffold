from __future__ import annotations

from typing import Any

from .config import DomainConfig


def build_record_context(
    config: DomainConfig,
    generated_files: tuple[str, ...],
) -> dict[str, Any]:
    """Return deterministic, redacted values used by build-record templates."""
    return {
        "domain": config.domain,
        "services": config.services,
        "worktree": config.worktree,
        "generated_files": generated_files,
    }
