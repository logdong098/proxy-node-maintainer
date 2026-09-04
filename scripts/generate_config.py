#!/usr/bin/env python3
"""Render subs-check's config from a human-editable source list."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ROOT / "config" / "sources.txt"
DEFAULT_TEMPLATE = ROOT / "config" / "config.template.yaml"
DEFAULT_OUTPUT = ROOT / "config" / "config.yaml"
MARKER = "# __GENERATED_SUB_URLS__"


class SourceError(ValueError):
    pass


def parse_source_line(raw_line: str, line_number: int) -> str | None:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None

    url_part, separator, label_part = line.partition("|")
    url = url_part.strip()
    label = label_part.strip() if separator else ""
    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SourceError(
            f"sources.txt 第 {line_number} 行不是有效的 HTTP(S) URL: {url!r}"
        )
    if any(char.isspace() for char in url):
        raise SourceError(f"sources.txt 第 {line_number} 行 URL 含空白字符")
    if "#" in url:
        raise SourceError(
            f"sources.txt 第 {line_number} 行 URL 已包含 #；请改用无 fragment 的地址"
        )
    if label and any(char in label for char in "\r\n#"):
        raise SourceError(f"sources.txt 第 {line_number} 行标签包含不支持的字符")

    return f"{url}#{label}" if label else url


def load_sources(path: Path) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        source = parse_source_line(raw_line, line_number)
        if source and source not in seen:
            seen.add(source)
            sources.append(source)
    if not sources:
        raise SourceError(f"{path} 中没有可用的数据源")
    return sources


def render(template: str, sources: list[str]) -> str:
    if template.count(MARKER) != 1:
        raise SourceError(f"模板必须且只能包含一个标记：{MARKER}")
    rendered_sources = "\n".join(
        f"  - {json.dumps(source, ensure_ascii=False)}" for source in sources
    )
    return template.replace(MARKER, rendered_sources) + ("" if template.endswith("\n") else "\n")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary_path = Path(handle.name)
    os.replace(temporary_path, path)


def generate(sources_path: Path, template_path: Path, output_path: Path) -> int:
    sources = load_sources(sources_path)
    template = template_path.read_text(encoding="utf-8")
    atomic_write(output_path, render(template, sources))
    print(f"已生成 {output_path}，共 {len(sources)} 个数据源")
    return len(sources)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    generate(args.sources, args.template, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
