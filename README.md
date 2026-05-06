# Repo2RLEnv

**Turn any repository into an RL environment for training and evaluation.**

Repo2RLEnv synthesizes verifiable data from existing repositories using a variety of methods, exports it into a uniform spec, and lets you train models, evaluate agents, and publish straight to the Hugging Face Hub. End-to-end — **synthesis, training, eval, export** — with the main focus on training. The uniform spec is [Harbor](https://github.com/harbor-framework/harbor)'s, so the datasets you produce drop straight into any Harbor-compatible runtime as well.

```
  ╭──────────────╮     ╭──────────────╮     ╭──────────────╮     ╭──────────────────╮
  │     any      │ ──▶ │  synthesize  │ ──▶ │ uniform spec │ ──▶ │ train · eval ·   │
  │     repo     │     │  (pipelines) │     │   (Harbor)   │     │  push to HF Hub  │
  ╰──────────────╯     ╰──────────────╯     ╰──────────────╯     ╰──────────────────╯
                       └──────────────────────── Repo2RLEnv ────────────────────────┘
```

---

## Quickstart

```bash
# Install (pick one)
uv add repo2rlenv                                 # add to a uv-managed project
uvx repo2rlenv --help                           # one-shot, no install
pip install repo2rlenv                            # classic

# Generate
repo2rlenv generate https://github.com/django/django \
  --pipeline pr_mining --limit 100 --out ./datasets/django

# Validate
repo2rlenv validate ./datasets/django

# Push to the Hub
repo2rlenv push ./datasets/django --hub-repo-id myorg/django-r2e

# Evaluate any agent
repo2rlenv eval ./datasets/django --agent claude-code

# Train any model
repo2rlenv train ./datasets/django --trainer trl --model Qwen/Qwen2.5-Coder-7B
```

One CLI. Five verbs. No glue code.

---

## Pipelines

The heart of Repo2RLEnv. Different ways to manufacture verifiable tasks from the same repo — pick one, pick all, write your own.

| Pipeline | What it does |
|---|---|
| **`pr_mining`** | Walks merged PRs, replays each one in an isolated sandbox, captures the test that the PR makes pass — that test becomes the reward |
| **`mutation`** | Mutates the codebase, keeps mutations that break ≥1 existing test, lets an LLM author the resulting issue |
| **`issue_gen`** | LLM proposes plausible issues from existing code, then mutates the repo to make them real and solvable |
| **`<your_plugin>`** | Drop in a third-party pipeline via Python entry points |

Every pipeline flows through the same 4-layer quality gate — environment determinism, oracle consistency, LLM-judge semantic alignment, false-negative filtering — before a task is admitted to the dataset. Junk in, junk out is the default in this space; Repo2RLEnv's QA is what stops it.

---

## What you get out

A single dataset format that:

- Is **verifiable** — every task carries an executable test that produces a real reward signal
- Is **reproducible** — pinned image digests, deterministic verifiers, content-addressed
- **Trains anywhere** — TRL, SkyRL, Prime-RL, Tinker, Miles, Slime, harbor.rl
- **Evaluates anywhere** — Claude Code, OpenHands, Codex CLI, Gemini CLI, Mini-SWE-Agent, your own agent
- Is **language-agnostic** — Dockerfile + shell verifier; not Python-only
- **Publishes natively** to Hugging Face Hub, public or private
- Supports **private repos** end-to-end (auth, build secrets declared, verifier-time secrets forbidden)

---

## Under the hood

Repo2RLEnv emits datasets in the [Harbor](https://github.com/harbor-framework/harbor) task format — a battle-tested, language-agnostic spec with an existing ecosystem of sandboxes, agent harnesses, and training-framework integrations. By targeting Harbor we inherit its full stack: Local Docker / Modal / Daytona / E2B / Runloop sandboxes, every major coding-agent harness, parallel execution, registry CLI, and downstream hooks for [OpenReward](https://docs.openreward.ai) (which adds Miles, Slime, etc.). A small `[metadata.repo2rlenv]` extension carries provenance, image digests, and pipeline lineage.

We don't reinvent the spec — we generate the data that goes into it.

---

## Why Repo2RLEnv

The synthesis-of-coding-tasks landscape compared:

| | Repo2RLEnv | SWE-bench | SWE-Bench++ | SWE-smith |
|---|:-:|:-:|:-:|:-:|
| Point at any repo | ✅ | ✗ (12 curated) | ✅ | ✅ |
| Real PR mining | ✅ | ✅ | ✅ | ✗ |
| Synthetic mutation | ✅ | ✗ | ✗ | ✅ |
| 4-layer QA gate | ✅ | manual | ✅ | partial |
| Polyglot from day one | ✅ | Python | Python | Python-dominant |
| Plugs into existing trainers | ✅ | ✗ | ✗ | SWE-agent only |
| HF Hub native | ✅ | partial | ✗ | ✗ |

The wedge: **PR mining + synthetic mutation under one quality-gated pipeline, language-agnostic, dropping straight into the trainers and harnesses people already use.**

---

## Status

Pre-alpha. `pr_mining` + Local Docker + HF Hub push works end-to-end on Python repos.

## Credits

Repo2RLEnv stands on shoulders:

- [Harbor](https://github.com/harbor-framework/harbor) — the task format and runtime ecosystem we adopt
- [OpenReward](https://docs.openreward.ai) — ORS protocol layer above Harbor; extra trainer integrations
- [SWE-bench](https://github.com/SWE-bench/SWE-bench) / [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) — original PR-as-task formulation
- [SWE-Bench++](https://arxiv.org/abs/2512.17419) — four-stage QA pipeline we re-implement
- [SWE-smith](https://github.com/SWE-bench/SWE-smith) — mutation-based synthesis
- [verifiers](https://github.com/willccbb/verifiers) (Prime Intellect), [OpenEnv](https://github.com/meta-pytorch/OpenEnv) (Meta + HF) — adjacent standardization efforts

## License

Apache 2.0 — see [LICENSE](./LICENSE).
