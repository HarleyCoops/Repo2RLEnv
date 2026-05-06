"""Repo2RLEnv CLI — placeholder commands for the v0.1.0 scaffolding."""

from __future__ import annotations

import argparse
import sys

from repo2rlenv import __version__

_COMMANDS: list[tuple[str, str]] = [
    ("generate", "Synthesize tasks from a repository"),
    ("validate", "Validate a dataset against the spec"),
    ("push", "Push a dataset to the Hugging Face Hub"),
    ("eval", "Evaluate an agent against a dataset"),
    ("train", "Train a model against a dataset"),
]


def _stub(name: str) -> int:
    print(f"repo2rlenv {name}: not yet implemented in v{__version__}.")
    print("Track progress at https://github.com/adithya-s-k/Repo2RLEnv")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="repo2rlenv",
        description="Turn any repository into an RL environment for training and evaluation.",
    )
    parser.add_argument(
        "--version", action="version", version=f"repo2rlenv {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for name, help_ in _COMMANDS:
        cmd = sub.add_parser(name, help=help_)
        cmd.add_argument("args", nargs="*", help=argparse.SUPPRESS)

    args = parser.parse_args(argv)
    return _stub(args.command)


if __name__ == "__main__":
    sys.exit(main())
