#!/usr/bin/env python3
"""Create local secrets once and render the runtime configuration."""

from __future__ import annotations

from pathlib import Path
import secrets

from generate_config import ROOT, generate, DEFAULT_OUTPUT, DEFAULT_SOURCES, DEFAULT_TEMPLATE


ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"


def create_env() -> bool:
    if ENV_PATH.exists():
        return False
    template = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    api_key = secrets.token_urlsafe(32)
    ENV_PATH.write_text(template.replace("replace-me", api_key), encoding="utf-8")
    ENV_PATH.chmod(0o600)
    return True


def main() -> int:
    created = create_env()
    generate(DEFAULT_SOURCES, DEFAULT_TEMPLATE, DEFAULT_OUTPUT)
    if created:
        print("已生成仅限本机使用的 .env 和随机 API_KEY")
    else:
        print("保留已有 .env，未覆盖 API_KEY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
