from pathlib import Path
import tempfile
import unittest

from scripts.generate_config import SourceError, load_sources, parse_source_line, render


class SourceParsingTests(unittest.TestCase):
    def test_comments_and_blank_lines_are_ignored(self):
        self.assertIsNone(parse_source_line("# comment", 1))
        self.assertIsNone(parse_source_line("  ", 2))

    def test_label_is_appended_as_subs_check_annotation(self):
        value = parse_source_line("https://example.com/sub | source-a", 3)
        self.assertEqual(value, "https://example.com/sub#source-a")

    def test_non_http_source_is_rejected(self):
        with self.assertRaises(SourceError):
            parse_source_line("file:///tmp/nodes.txt", 4)

    def test_duplicates_are_removed_without_reordering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.txt"
            path.write_text(
                "https://a.example/sub\nhttps://a.example/sub\nhttps://b.example/sub\n",
                encoding="utf-8",
            )
            self.assertEqual(
                load_sources(path),
                ["https://a.example/sub", "https://b.example/sub"],
            )


class RenderingTests(unittest.TestCase):
    def test_sources_are_rendered_as_yaml_compatible_strings(self):
        template = "sub-urls:\n# __GENERATED_SUB_URLS__\n"
        result = render(template, ["https://example.com/sub#来源"])
        self.assertIn('  - "https://example.com/sub#来源"', result)

    def test_missing_marker_is_rejected(self):
        with self.assertRaises(SourceError):
            render("sub-urls:\n", ["https://example.com/sub"])


if __name__ == "__main__":
    unittest.main()
