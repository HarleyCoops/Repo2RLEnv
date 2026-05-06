"""Write Harbor-compliant task directories.

The lite path emits a minimal Harbor task:
  task.toml + instruction.md + solution/patch.diff
No environment/, no tests/. Reward kind = "diff_similarity" only.

----------------------------------------------------------------------------
Acknowledgment
----------------------------------------------------------------------------
The output FORMAT (task.toml schema, directory layout, /logs/verifier/reward.txt
contract, [metadata] tables) is defined by:

  Harbor Framework (Laude Institute / Terminal-Bench creators)
  https://github.com/harbor-framework/harbor    (Apache-2.0)
  https://www.harborframework.com/docs/tasks

We emit Harbor's format directly so any Harbor-compatible runtime, agent
harness, or downstream framework (OpenReward, SkyRL via Harbor, etc.) can
consume our datasets unchanged. We do NOT depend on the `harbor` Python
package — we generate the file format from scratch. The format itself is a
spec (data layout); using it does not require a license grant. Repo2RLEnv-
specific provenance lives inside Harbor's free-form `[metadata]` table under
the namespaced subtable `[metadata.repo2env]`.

Released under Apache-2.0.
----------------------------------------------------------------------------
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w


@dataclass(slots=True)
class HarborTask:
    name: str
    org: str
    description: str
    instruction: str
    oracle_diff: str
    repo2env: dict[str, Any]
    difficulty: str = "medium"
    category: str = "bugfix"
    keywords: list[str] = field(default_factory=list)


def _content_hash(task: HarborTask) -> str:
    h = hashlib.sha256()
    h.update(task.instruction.encode("utf-8"))
    h.update(b"\0")
    h.update(task.oracle_diff.encode("utf-8"))
    return f"sha256:{h.hexdigest()}"


def write_harbor_task(task: HarborTask, dest_dir: Path) -> Path:
    """Materialize the task directory at dest_dir/<task.name>. Returns the path."""
    task_path = dest_dir / task.name
    task_path.mkdir(parents=True, exist_ok=True)

    # task.toml
    repo2env = dict(task.repo2env)
    repo2env.setdefault("spec_version", "0.1.0")
    repo2env.setdefault("content_hash", _content_hash(task))
    repo2env.setdefault("reward_kinds", ["diff_similarity"])

    payload: dict[str, Any] = {
        "version": "1.0",
        "task": {
            "name": task.name,
            "org": task.org,
            "description": task.description,
        },
        "metadata": {
            "difficulty": task.difficulty,
            "category": task.category,
            "keywords": task.keywords,
            "repo2env": repo2env,
        },
        "agent": {"timeout_sec": 1800.0},
        "verifier": {"timeout_sec": 300.0},
    }
    (task_path / "task.toml").write_bytes(tomli_w.dumps(payload).encode("utf-8"))

    # instruction.md
    (task_path / "instruction.md").write_text(task.instruction, encoding="utf-8")

    # solution/patch.diff
    sol_dir = task_path / "solution"
    sol_dir.mkdir(exist_ok=True)
    (sol_dir / "patch.diff").write_text(task.oracle_diff, encoding="utf-8")

    return task_path
