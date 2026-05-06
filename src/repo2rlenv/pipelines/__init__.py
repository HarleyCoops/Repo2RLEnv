"""Pipeline implementations + the standardized contract."""

from repo2rlenv.pipelines.base import Pipeline, PipelineResult
from repo2rlenv.pipelines.pr_mining_lite import PRMiningLitePipeline

PIPELINES: dict[str, type[Pipeline]] = {
    "pr_mining_lite": PRMiningLitePipeline,
}

__all__ = ["PIPELINES", "Pipeline", "PipelineResult", "PRMiningLitePipeline"]
