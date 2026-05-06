"""Pipeline contract — every synthesis pipeline implements this Protocol.

A pipeline:
  1. Takes a `GenerationInput` (the standard input shape) plus its own Options
     model (the validated kwargs).
  2. Emits Harbor-compatible task directories at `out_dir`.
  3. Returns a `PipelineResult` with candidate / emitted / skipped counters
     so the CLI can report yield + QA pass rates uniformly.

Adding a new pipeline = subclass-by-protocol (just match the shape) + register
in `PIPELINES` and `OPTIONS_REGISTRY`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Protocol, runtime_checkable

from pydantic import BaseModel

from repo2rlenv.spec.input import GenerationInput, PipelineName


@dataclass(slots=True)
class PipelineResult:
    """Uniform result shape across every pipeline.

    Attributes:
        candidates: Total candidates discovered before filtering.
        emitted: Tasks actually written to `out_dir`.
        skipped: Sum of skip-reason counts.
        out_dir: Where tasks landed.
        skip_reasons: Per-reason counts, e.g. {"draft": 3, "too_many_files": 2}.
    """

    candidates: int
    emitted: int
    skipped: int
    out_dir: Path
    skip_reasons: dict[str, int]


@runtime_checkable
class Pipeline(Protocol):
    """The contract every synthesis pipeline implements.

    Implementations are duck-typed (Protocol, not ABC) so a class doesn't have
    to inherit from anything — just expose:

      - `name: ClassVar[PipelineName]` — the registered identifier
      - `__init__(input: GenerationInput, options: <Options>) -> None`
      - `run(out_dir: Path) -> PipelineResult`

    The `Options` arg is whatever Pydantic model is registered for `name` in
    `OPTIONS_REGISTRY`. The dispatcher in `cli.cmd_generate` validates and
    instantiates both before calling `run()`.
    """

    name: ClassVar[PipelineName]

    def __init__(self, input: GenerationInput, options: BaseModel) -> None: ...

    def run(self, out_dir: Path) -> PipelineResult: ...
