#!/usr/bin/env python3
"""Validate local files before Docker Compose starts the service."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from generate_config import ROOT, load_sources, DEFAULT_SOURCES


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    errors: list[str] = []
    env_path = ROOT / ".env"
    config_path = ROOT / "config" / "config.yaml"

    if shutil.which("docker") is None:
        errors.append("未找到 docker")
    if not env_path.exists():
        errors.append("缺少 .env，请先运行 python3 scripts/bootstrap.py")
    else:
        api_key = read_env(env_path).get("API_KEY", "")
        if len(api_key) < 24 or api_key == "replace-me":
            errors.append("API_KEY 未生成或长度不足 24 个字符")
    if not config_path.exists():
        errors.append("缺少 config/config.yaml，请先运行配置生成器")

    try:
        source_count = len(load_sources(DEFAULT_SOURCES))
    except Exception as exc:  # preflight should aggregate all actionable failures
        errors.append(str(exc))
        source_count = 0

    if errors:
        for error in errors:
            print(f"错误: {error}")
        return 1

    subprocess.run(
        ["docker", "compose", "config", "--quiet"], cwd=ROOT, check=True
    )
    print(f"预检通过：{source_count} 个数据源，Compose 配置有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
