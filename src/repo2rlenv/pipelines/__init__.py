"""Pipeline implementations + the standardized contract."""

from repo2rlenv.pipelines.base import Pipeline, PipelineResult
from repo2rlenv.pipelines.pr_diff import PRDiffPipeline

PIPELINES: dict[str, type[Pipeline]] = {
    "pr_diff": PRDiffPipeline,
}

__all__ = ["PIPELINES", "Pipeline", "PipelineResult", "PRDiffPipeline"]
