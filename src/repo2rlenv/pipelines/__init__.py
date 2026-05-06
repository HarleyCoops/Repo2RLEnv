"""Pipeline implementations."""

from repo2rlenv.pipelines.pr_mining_lite import PRMiningLitePipeline

PIPELINES = {
    "pr_mining_lite": PRMiningLitePipeline,
}

__all__ = ["PIPELINES", "PRMiningLitePipeline"]
