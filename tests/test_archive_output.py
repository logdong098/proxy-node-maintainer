from pathlib import Path
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "config" / "archive_output.sh"


class ArchiveOutputTests(unittest.TestCase):
    def run_archive(self, output_dir: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["OUTPUT_DIR"] = str(output_dir)
        env["SNAPSHOT_RETENTION_DAYS"] = "14"
        return subprocess.run(
            ["sh", str(SCRIPT)], env=env, text=True, capture_output=True, check=True
        )

    def test_valid_output_updates_last_good_and_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            content = "proxies:\n  - name: example\n"
            (output_dir / "all.yaml").write_text(content, encoding="utf-8")
            self.run_archive(output_dir)
            self.assertEqual(
                (output_dir / "last-good.yaml").read_text(encoding="utf-8"), content
            )
            self.assertEqual(len(list((output_dir / "snapshots").glob("all-*.yaml"))), 1)

    def test_invalid_output_does_not_replace_last_good(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            (output_dir / "all.yaml").write_text("", encoding="utf-8")
            (output_dir / "last-good.yaml").write_text("previous", encoding="utf-8")
            self.run_archive(output_dir)
            self.assertEqual(
                (output_dir / "last-good.yaml").read_text(encoding="utf-8"),
                "previous",
            )


if __name__ == "__main__":
    unittest.main()
