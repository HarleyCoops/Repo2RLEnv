"""Top-level input contract — same shape across every pipeline."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class PipelineName(StrEnum):
    PR_MINING_LITE = "pr_mining_lite"
    PR_MINING = "pr_mining"
    COMMIT_MINING = "commit_mining"
    MUTATION = "mutation"
    OSS_INSTRUCT = "oss_instruct"
    EQUIVALENCE_TESTS = "equivalence_tests"
    LIVE_PR_MINING = "live_pr_mining"
    CVE_MINING = "cve_mining"
    REFACTOR_SYNTHESIS = "refactor_synthesis"


class RepoSpec(BaseModel):
    url: str
    ref: str = "HEAD"
    access: Literal["public", "private", "auto"] = "auto"
    auth_token_env: str | None = None
    sparse_paths: list[str] | None = None

    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        v = v.strip()
        if "/" not in v:
            raise ValueError(f"repo url must be 'owner/name' or full URL, got {v!r}")
        if not v.startswith(("http://", "https://", "git@")):
            v = f"https://github.com/{v}"
        return v.rstrip("/").removesuffix(".git")

    @property
    def owner_name(self) -> tuple[str, str]:
        """Return (owner, name) parsed from the URL."""
        path = self.url.replace("https://github.com/", "").replace("git@github.com:", "")
        parts = path.rstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"cannot parse owner/name from {self.url!r}")
        return parts[-2], parts[-1]


class LLMSpec(BaseModel):
    provider: str
    model: str
    api_key_env: str | None = None
    endpoint: str | None = None
    max_concurrent: int = 5
    timeout_sec: int = 120
    fallback: LLMSpec | None = None

    @property
    def qualified_name(self) -> str:
        """LiteLLM-compatible 'provider/model' string."""
        # Some providers (huggingface) use a different format
        if self.provider in ("openai", "anthropic", "huggingface"):
            return f"{self.provider}/{self.model}"
        return f"{self.provider}/{self.model}"


class QALayer(StrEnum):
    DETERMINISM = "determinism"
    ORACLE_CONSISTENCY = "oracle_consistency"
    LLM_JUDGE = "llm_judge"
    FALSE_NEGATIVE = "false_negative"
    DIFF_PARSE = "diff_parse"  # lite-pipeline-only: oracle diff must apply cleanly


class QASpec(BaseModel):
    enabled: bool = True
    layers: list[QALayer] = Field(default_factory=lambda: [QALayer.DIFF_PARSE])
    judge_llm: LLMSpec | None = None
    determinism_runs: int = 3
    oracle_runs: int = 3
    skip_on_fail: bool = True


class SandboxSpec(BaseModel):
    """Sandbox config — describes what a pipeline needs at generation time.

    Repo2RLEnv ships NO sandbox runtime. This spec just records what the
    pipeline requests; the dispatch happens externally:

    - `provider="none"` (default for lite pipelines) — no execution at gen
      time. Lite consumption is also runtime-free (just `repo2rlenv reward`).

    - `provider="harbor"` (full pipelines like `pr_mining`) — at gen time we
      shell out to `harbor` with `harbor_provider` selecting the underlying
      backend (Local Docker / Modal / Daytona / E2B / Runloop). Consumers
      run tasks via `harbor run -d <dataset> -e <provider> ...` directly.
    """

    provider: Literal["none", "harbor"] = "none"
    harbor_provider: Literal["local", "modal", "daytona", "e2b", "runloop"] = "local"
    concurrency: int = 10
    network: Literal["open", "build_open_run_restricted", "none"] = "build_open_run_restricted"
    gpu: GPUSpec | None = None
    image_registry: str | None = None
    timeout_sec: int = 600


class GPUSpec(BaseModel):
    """GPU request, lowered to the Harbor provider's native config.

    Only meaningful for full sandbox-required pipelines (`pr_mining` etc.)
    on ML repositories whose test suites require CUDA. Lite pipelines never
    use this. Provider support varies:
      - Modal:   rich (a10g, a100, h100, ...)
      - Daytona: yes
      - Runloop: yes (limited)
      - E2B:     limited (CPU primarily)
      - Local:   only if host has GPU + nvidia-container-runtime
    """

    count: int = 1
    kind: Literal["any", "a10g", "a100", "h100", "l4", "t4"] = "any"


class OutputSpec(BaseModel):
    destination: str
    org: str
    dataset_name: str
    visibility: Literal["public", "private"] = "public"


class AuthSpec(BaseModel):
    github_token_env: str = "GITHUB_TOKEN"
    use_gh_cli: bool = True
    hf_token_env: str = "HF_TOKEN"
    use_hf_cli: bool = True
    build_secrets_env: dict[str, str] = Field(default_factory=dict)


class PipelineSpec(BaseModel):
    name: PipelineName
    options: dict[str, Any] = Field(default_factory=dict)


class GenerationInput(BaseModel):
    spec_version: Literal["0.1.0"] = "0.1.0"
    repo: RepoSpec
    pipeline: PipelineSpec
    llm: LLMSpec
    output: OutputSpec
    qa: QASpec = Field(default_factory=QASpec)
    sandbox: SandboxSpec = Field(default_factory=SandboxSpec)
    auth: AuthSpec = Field(default_factory=AuthSpec)


LLMSpec.model_rebuild()
SandboxSpec.model_rebuild()
