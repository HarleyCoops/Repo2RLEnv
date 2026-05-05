# Repo2Env

**Turn any GitHub repository into an RL environment for training your LLM.**

Point Repo2Env at a repo. It walks the git history, mines real PRs (or synthesizes new tasks), wraps each one in a reproducible sandbox, and emits a standardized, verifiable task dataset you can train on, evaluate against, or push straight to the Hugging Face Hub.

```
                 ┌─────────────┐
  any repo  ───► │  Repo2Env │ ───►  RL-ready task dataset
                 └─────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
   Generate         Standardize      Consume
   (pipelines)     (Task spec)    (sandboxes + exporters)
```

---

## Quickstart

```bash
pip install repo2env

# 1. Generate tasks from a repo
repo2env generate https://github.com/django/django \
  --pipeline pr_mining \
  --sandbox modal \
  --limit 100 \
  --out ./datasets/django

# 2. Validate the dataset against the spec
repo2env validate ./datasets/django

# 3. Run a single task end-to-end
repo2env run ./datasets/django/tasks/django__12345 --agent claude-code

# 4. Export to your favorite RL framework
repo2env export ./datasets/django --format openenv --out ./envs/

# 5. Push to the Hub
repo2env push ./datasets/django --hub-repo-id myorg/django-r2e
```

---

## How it works

Repo2Env is built around one rock-solid idea: **a single Task spec sits in the middle, and everything else is pluggable.**

### 1. Generation — pipelines that produce tasks

| Pipeline | What it does |
|---|---|
| `pr_mining` | Walks merged PRs, replays each in a sandbox, captures fail-to-pass tests as the oracle |
| `mutation` | Mutates the codebase, keeps mutations that break ≥1 test, lets an LLM author the issue |
| `issue_gen` | LLM proposes issues from existing code, then mutates to make them solvable |
| *(plugin)* | Third-party pipelines via Python entry points |

### 2. Spec — the immovable middle

Every pipeline outputs the same versioned, schema-validated Task. Each task is self-contained:

```
django__12345/
├── task.yaml              # spec_version, provenance, reward config
├── instruction.md         # what the agent is asked to do
├── env/Dockerfile         # reproducible environment
├── tests/test.sh          # verifier — writes reward to /logs/reward.txt
└── solution/patch.diff    # reference oracle (optional)
```

Datasets ship to the Hub as parquet metadata + LFS-tracked task directories — query the headers fast, pull the artifacts on demand:

```python
from datasets import load_dataset
ds = load_dataset("myorg/django-r2e")        # fast metadata view

import repo2env
tasks = repo2env.load("myorg/django-r2e") # full tasks with files
```

### 3. Consumption — sandboxes and exporters, independently swappable

**Sandboxes** answer *where* the Docker runs. The same task runs anywhere.

| Sandbox | Status | Best for |
|---|---|---|
| Local Docker | v0.1 | Dev, smoke tests |
| Modal | v0.2 | Generation at scale |
| E2B | v0.3 | Fast RL rollouts |
| Daytona | v1.0 | Harbor parity |
| EC2 | v1.0 | Cheap large-scale builds |
| HF Spaces | v1.0 | Hub-native deployment |

**Exporters** answer *what shape* the task takes for downstream RL frameworks.

| Exporter | Target |
|---|---|
| `harbor` | Harbor task directory (native shape) |
| `openenv` | OpenEnv FastAPI server in Docker (Meta + HF) |
| `verifiers` | `load_environment()` Python module (Prime Intellect) |
| `ors` | Open Reward Standard / MCP-compatible |

You can mix and match: generate with `pr_mining` on Modal, export to OpenEnv, run rollouts on E2B. Three independent dimensions.

---

## Why another framework?

| | Repo2Env | SWE-bench | SWE-smith | Harbor | verifiers |
|---|:-:|:-:|:-:|:-:|:-:|
| Point at any repo | ✅ | ✗ (curated set) | ✅ | ✗ | ✗ |
| Real PR mining | ✅ | ✅ | ✗ | ✗ | ✗ |
| Synthetic mutation | ✅ | ✗ | ✅ | ✗ | ✗ |
| Polyglot from day one | ✅ | Python | Python-dominant | ✅ | ✅ |
| Standardized task spec | ✅ | partial | partial | ✅ | ✅ |
| HF Hub native publish | ✅ | ✗ | ✗ | ✗ | partial |
| Multi-sandbox runtime | ✅ | ✗ | ✗ | partial | ✗ |
| Multi-exporter | ✅ | ✗ | ✗ | ✗ | ✗ |

Repo2Env is the first framework that treats **generation, spec, and consumption as three independently pluggable layers** — so you're never locked to one pipeline, one sandbox, or one trainer.

---

## Status

**Pre-alpha.** v0.1 ships: `pr_mining` + Local Docker + Harbor exporter + HF Hub push. End-to-end on Python repos.

See [`SCHEMA.md`](./SCHEMA.md) for the Task spec. See [`ROADMAP.md`](./ROADMAP.md) for what's next.

## Inspiration & credits

Repo2Env stands on the shoulders of:

- [SWE-bench](https://github.com/SWE-bench/SWE-bench) and [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) — the original PR-as-task formulation
- [SWE-Bench++](https://arxiv.org/abs/2512.17419) — the four-stage QA pipeline
- [SWE-smith](https://github.com/SWE-bench/SWE-smith) — mutation-based task synthesis
- [Harbor](https://github.com/harbor-framework/harbor) — declarative task directory layout
- [OpenEnv](https://github.com/meta-pytorch/OpenEnv) — Gymnasium-style RL spec from Meta + HF
- [verifiers](https://github.com/willccbb/verifiers) — Rubric-based reward design from Prime Intellect
- [Open Reward Standard](https://docs.openreward.ai) — MCP-extended RL primitives

## License

Apache 2.0 — see [LICENSE](./LICENSE).
