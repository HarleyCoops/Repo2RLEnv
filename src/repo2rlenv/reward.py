"""Diff-similarity reward.

Computes a [0, 1] score by comparing a predicted unified diff against an oracle
diff using sequence similarity. Verifiable: identical diffs ⇒ 1.0; unrelated
diffs ⇒ near 0. Uses only stdlib (`difflib`).

----------------------------------------------------------------------------
Acknowledgment
----------------------------------------------------------------------------
The reward concept (sequence-similarity over normalized diffs) is inspired by:

  SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software
  Evolution (Wei et al., NeurIPS '25, arXiv:2502.18449)
  https://github.com/facebookresearch/swe-rl
  Reward library license: CC BY-NC 4.0 (non-commercial)

This file is an INDEPENDENT REIMPLEMENTATION. No code is copied from SWE-RL —
we use only Python's standard library (`difflib.SequenceMatcher`). The CC
BY-NC license therefore does not apply to this file. This file is released
under Apache-2.0 along with the rest of Repo2RLEnv. See LICENSE at repo root.
----------------------------------------------------------------------------
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass


_HUNK_HEADER_RE = re.compile(r"^@@.*@@")
_FILE_HEADER_RE = re.compile(r"^(?:---|\+\+\+) ")
_INDEX_LINE_RE = re.compile(r"^index ")
_DIFF_GIT_RE = re.compile(r"^diff --git ")


@dataclass(slots=True)
class DiffRewardMetadata:
    similarity: float
    pred_lines: int
    oracle_lines: int
    matched_lines: int
    parse_error: str | None = None


def _normalize_diff(diff: str) -> list[str]:
    """Strip volatile metadata (hunk line numbers, indices, file headers context)."""
    lines: list[str] = []
    for line in diff.splitlines():
        if _DIFF_GIT_RE.match(line):
            continue
        if _INDEX_LINE_RE.match(line):
            continue
        if _HUNK_HEADER_RE.match(line):
            lines.append("@@")  # keep as a separator but drop line numbers
            continue
        if _FILE_HEADER_RE.match(line):
            # Keep filename markers but normalize whitespace
            lines.append(line.split("\t")[0].strip())
            continue
        lines.append(line)
    return lines


def calculate_diff_similarity_reward(
    oracle_diff: str, predicted_diff: str
) -> tuple[float, DiffRewardMetadata]:
    """Score a predicted diff against an oracle diff.

    Returns (reward, metadata) where reward ∈ [0, 1]:
      - 1.0 if normalized diffs are identical
      - 0.0 if predicted_diff is empty or unparseable
      - else difflib.SequenceMatcher ratio over normalized lines
    """
    if not predicted_diff.strip():
        return 0.0, DiffRewardMetadata(0.0, 0, 0, 0, "empty prediction")

    oracle_lines = _normalize_diff(oracle_diff)
    pred_lines = _normalize_diff(predicted_diff)

    if not oracle_lines:
        return 0.0, DiffRewardMetadata(
            0.0, len(pred_lines), 0, 0, "empty oracle after normalization"
        )

    matcher = difflib.SequenceMatcher(a=oracle_lines, b=pred_lines, autojunk=False)
    ratio = matcher.ratio()
    matched = sum(triple.size for triple in matcher.get_matching_blocks())

    return ratio, DiffRewardMetadata(
        similarity=ratio,
        pred_lines=len(pred_lines),
        oracle_lines=len(oracle_lines),
        matched_lines=matched,
    )
