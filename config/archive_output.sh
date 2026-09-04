#!/bin/sh
set -eu

output_dir="${OUTPUT_DIR:-/app/output}"
retention_days="${SNAPSHOT_RETENTION_DAYS:-14}"
source_file="$output_dir/all.yaml"
snapshot_dir="$output_dir/snapshots"

# 只有看起来像有效 Clash 订阅且非空时，才更新 last-good。
if [ ! -s "$source_file" ] || ! grep -q '^proxies:' "$source_file"; then
  echo "archive: all.yaml 为空或格式异常，保留现有 last-good.yaml"
  exit 0
fi

mkdir -p "$snapshot_dir"
timestamp="$(date -u '+%Y%m%dT%H%M%SZ')"
cp "$source_file" "$output_dir/last-good.yaml"
cp "$source_file" "$snapshot_dir/all-$timestamp.yaml"

for candidate in base64.txt mihomo.yaml; do
  if [ -s "$output_dir/$candidate" ]; then
    stem="${candidate%.*}"
    suffix="${candidate##*.}"
    cp "$output_dir/$candidate" "$output_dir/last-good-$candidate"
    cp "$output_dir/$candidate" "$snapshot_dir/$stem-$timestamp.$suffix"
  fi
done

find "$snapshot_dir" -type f -mtime "+$retention_days" -delete
echo "archive: 已更新 last-good 和快照 $timestamp"
