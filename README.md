# Repo2RLEnv

**Turn any repository into an RL environment for training and evaluation.**

Repo2RLEnv synthesizes verifiable data from existing repositories using pluggable pipelines, exports it into a uniform spec, and pushes straight to the Hugging Face Hub. End-to-end — **synthesis → standardize → train + eval** — with the focus on training. The uniform spec is [Harbor](https://github.com/harbor-framework/harbor)'s, so the datasets you produce drop straight into any Harbor-compatible runtime.

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
uvx repo2rlenv --help                             # one-shot, no install
pip install repo2rlenv                            # classic

# Auth: nothing to set up if you've done `gh auth login` and `huggingface-cli login`
# Otherwise:  export GITHUB_TOKEN=... ; export HF_TOKEN=...

# Generate a dataset locally
repo2rlenv generate \
  --repo <owner>/<repo> \
  --pipeline pr_diff \
  --pipeline-opt limit=5 \
  --llm anthropic/claude-sonnet-4-6 \
  --out ./datasets/<dataset-name>

# Or push straight to HF Hub with --out hf://<your-org>/<dataset-name>

# Validate a local dataset against the spec
repo2rlenv validate ./path/to/dataset

# Score a candidate diff against a task's oracle (diff-similarity reward)
repo2rlenv reward --task ./datasets/<dataset-name>/<task-id> --prediction ./candidate.diff

# Or write a sample config first and use --config
repo2rlenv init && repo2rlenv generate --config repo2rlenv.config.yaml
```

Full walkthrough in [**`docs/quickstart.md`**](./docs/quickstart.md).

---

## Pipelines

Different methods to manufacture verifiable tasks from a repo. Pick one, run it, push the dataset. Names follow `{source}_{shape}` — `_runtime` pipelines verify the oracle inside a sandbox; `_diff` doesn't.

| Pipeline | Status | Inspiration |
|---|---|---|
| [`pr_diff`](./docs/pipelines/pr_diff.md) | **shipped (v0.1)** | [SWE-RL](https://github.com/facebookresearch/swe-rl) |
| [`pr_runtime`](./docs/pipelines/pr_runtime.md) | planned (v0.3) | [SWE-bench](https://github.com/SWE-bench/SWE-bench) |
| [`commit_runtime`](./docs/pipelines/commit_runtime.md) | planned | [R2E-Gym SWE-GEN](https://github.com/R2E-Gym/R2E-Gym) |
| [`mutation_bugs`](./docs/pipelines/mutation_bugs.md) | planned | [SWE-smith](https://github.com/SWE-bench/SWE-smith) |
| [`code_instruct`](./docs/pipelines/code_instruct.md) | planned | [Magicoder](https://github.com/ise-uiuc/magicoder) |
| [`equivalence_tests`](./docs/pipelines/equivalence_tests.md) | planned | [R2E](https://github.com/r2e-project/r2e) |
| [`pr_stream`](./docs/pipelines/pr_stream.md) | planned | [SWE-bench-Live](https://github.com/microsoft/SWE-bench-Live) |
| [`cve_patches`](./docs/pipelines/cve_patches.md) | planned (v1.0) | [PatchSeeker](https://github.com/hungkien05/PatchSeeker) |
| [`refactor_synthesis`](./docs/pipelines/refactor_synthesis.md) | planned (v1.0) | RefactoringMiner |

Each pipeline is text-only or sandbox-required; all of them flow through the same QA gate (determinism, oracle consistency, LLM judge, false-negative filter) before tasks are admitted to a dataset. The text-only path (`pr_diff`) skips the heavy QA layers since there's no execution to validate.

See [**`docs/pipelines/README.md`**](./docs/pipelines/README.md) for the full status table including reward kinds, GPU needs, and sandbox requirements.

---

## What you get out

A dataset format that:

- Is **verifiable** — every task carries either an executable test (`test_execution`) or a stored oracle diff (`diff_similarity`); your trainer picks the reward type
- Is **content-addressed** — `content_hash` over each task; same artifacts ⇒ same hash
- **Trains anywhere via Harbor** — TRL, SkyRL, Prime-RL, Tinker, Miles, Slime, harbor.rl
- **Evaluates with any agent harness** — Claude Code, OpenHands, Codex CLI, Gemini CLI, …
- Is **language-agnostic** by spec — `_runtime` pipelines emit Dockerfile + shell verifier; `_diff` pipelines are pure text and work for any language with no extra config
- **Publishes natively** to Hugging Face Hub — `--out hf://owner/name` writes a Harbor-compatible `registry.json` so consumers can `harbor download` without any glue
- Supports **private repos** end-to-end — `gh auth token` resolved automatically; build secrets declared by name; verifier-time secrets forbidden by spec

---

## Under the hood

Repo2RLEnv emits datasets in the [Harbor](https://github.com/harbor-framework/harbor) task format. We don't ship our own sandbox, agent harness, or registry — Harbor already has those. We focus on **synthesis**: turning a real repo into verifiable, reproducible Harbor tasks. A small `[metadata.repo2env]` extension inside Harbor's `task.toml` carries provenance (pipeline name, base commit, PR URL, content hash, reward kinds, etc.).

For sandbox-required pipelines, an LLM agent ("bootstrap") iterates inside a fresh Docker container until the repo builds and tests can run; the working image is committed, cached, and reused across pipeline runs. See [`docs/reference/BOOTSTRAP.md`](./docs/reference/BOOTSTRAP.md).

By targeting Harbor we inherit its full stack: Local Docker / Modal / Daytona / E2B / Runloop sandboxes, every major coding-agent harness, parallel execution, the publishing CLI, and downstream hooks for [OpenReward](https://docs.openreward.ai) (which adds Miles, Slime to the trainer list).

---

## Documentation

Docs are organized into three tiers — see [`docs/README.md`](./docs/README.md) for the index.

- 🚀 [**`docs/quickstart.md`**](./docs/quickstart.md) — install → first dataset → push to Hub, in 10 minutes
- 📖 [**`docs/pipelines/`**](./docs/pipelines/README.md) — one page per synthesis pipeline (status, when to use, oracle shape, inspiration)
- 📚 Reference contracts and module-level API:
  - [`reference/SPEC.md`](./docs/reference/SPEC.md) — input/output contract
  - [`reference/API.md`](./docs/reference/API.md) — Python API for `src/repo2rlenv/`
  - [`reference/AUTH.md`](./docs/reference/AUTH.md) — GitHub / HF / LLM auth resolution
  - [`reference/BOOTSTRAP.md`](./docs/reference/BOOTSTRAP.md) — LLM-iterated per-repo Docker image
  - [`reference/AGENTS.md`](./docs/reference/AGENTS.md) — Harbor agent harnesses + RL trace plumbing
- 🛠 [**`contributing/ADDING_A_PIPELINE.md`**](./docs/contributing/ADDING_A_PIPELINE.md) — step-by-step cookbook for shipping a new pipeline

---

## Inspiration & related work

Repo2RLEnv borrows ideas from a constellation of repository-mining and RL-environment projects. Each pipeline name links to its primary inspiration; the table below collects the broader influences.

| Source | What we took |
|---|---|
| [SWE-RL](https://github.com/facebookresearch/swe-rl) (Wei et al., 2025) | The text-only PR-as-task with diff-similarity reward (`pr_diff`) |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) (Jimenez et al., 2024) | The full PR-as-task formulation that `pr_runtime` evolves |
| [SWE-bench-Live](https://github.com/microsoft/SWE-bench-Live) (Microsoft) | Continuous, post-cutoff PR mining (`pr_stream`) |
| [RepoLaunch](https://github.com/microsoft/RepoLaunch) (Microsoft) | LLM-agent-driven environment setup; our `bootstrap` is an independent reimplementation |
| [SWE-smith](https://github.com/SWE-bench/SWE-smith) | Mutation-based synthetic bug generation (`mutation_bugs`) |
| [SWE-Gym](https://github.com/SWE-Gym/SWE-Gym) | RL-environment framing for SWE-bench-style tasks |
| [R2E](https://github.com/r2e-project/r2e) / [R2E-Gym](https://github.com/R2E-Gym/R2E-Gym) | Equivalence-test synthesis (`equivalence_tests`) + repo-to-env iteration |
| [Magicoder / OSS-Instruct](https://github.com/ise-uiuc/magicoder) | Code-context → instruction synthesis (`code_instruct`) |
| [PatchSeeker / CVE-Bench](https://github.com/hungkien05/PatchSeeker) | CVE patches as training data (`cve_patches`) |
| [SWE-Bench++](https://arxiv.org/abs/2512.17419) | Four-stage QA pipeline we'll re-implement |
| [Harbor](https://github.com/harbor-framework/harbor) | Task format and runtime ecosystem we **adopt** as our output spec |
| [OpenReward](https://docs.openreward.ai) | ORS protocol + extra trainer integrations layered above Harbor |
| [verifiers](https://github.com/willccbb/verifiers) (Prime Intellect), [OpenEnv](https://github.com/meta-pytorch/OpenEnv) (Meta + HF) | Adjacent standardization efforts |

Every pipeline that draws from external work carries an Acknowledgment block in its `.py` file. No code is copied — implementations are independent and licensed Apache-2.0.

---

## Status

Pre-alpha.

- **v0.1** shipped on PyPI: `pr_diff` + HF Hub publish + diff-similarity reward, end-to-end on any GitHub repo (public or private). 71/71 tests passing.
- **v0.2** in main: bootstrap phase (LLM-driven Docker env), unified Rich UI, content-addressed cache, registry-qualified pullable digests.
- **v0.3** in flight: `pr_runtime` (sandbox-verified PR mining) + auto-trigger of bootstrap from `generate`.

## License

Apache 2.0 — see [LICENSE](./LICENSE).
