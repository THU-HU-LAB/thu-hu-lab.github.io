"""Offline regression checks for member-based citation inputs."""

import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from member_orcids import load_member_orcid


class MemberOrcidTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.member = Path(self.directory.name) / "member.md"

    def read(self, content):
        self.member.write_text(content, encoding="utf-8")
        return load_member_orcid(self.member)

    def test_only_orcid_is_forwarded_not_profile_fields(self):
        result = self.read(
            '\ufeff---\nname: 张三\nimage: portrait.jpg\n'
            'links:\n  orcid: "0000-0002-1825-0097"\n  email: test@example.org\n'
            '---\nBody with a colon: and [invalid YAML\n'
        )
        self.assertEqual(result, [{"orcid": "0000-0002-1825-0097"}])

    def test_missing_or_blank_orcid_is_skipped(self):
        for links in ('', 'links:\n', 'links: {}\n', 'links:\n  orcid:\n',
                      'links:\n  orcid: ""\n', 'links:\n  orcid: "  "\n'):
            with self.subTest(links=links):
                self.assertEqual(self.read(f"---\nname: Test\n{links}---\n"), [])

    def test_invalid_config_reports_member_path(self):
        for content in (
            "No front matter",
            "---\nname: Test\n",
            "---\nname: [\n---\n",
            "---\n- list\n---\n",
            "---\nlinks: wrong\n---\n",
            "---\nlinks:\n  orcid: 123\n---\n",
            "---\nlinks:\n  orcid: not-an-orcid\n---\n",
        ):
            with self.subTest(content=content):
                with self.assertRaisesRegex(ValueError, "member.md"):
                    self.read(content)

    def test_pipeline_reads_members_merges_manual_and_ignores_legacy_config(self):
        root = Path(self.directory.name)
        (root / "_members").mkdir()
        (root / "_data").mkdir()
        profile = ('---\nname: Test\nimage: avatar.jpg\nlinks:\n'
                   '  orcid: "0000-0002-1825-0097"\n---\nBiography\n')
        for name in ("one", "two"):
            (root / "_members" / f"{name}.md").write_text(profile)
        (root / "_members" / "blank.md").write_text("---\nname: Blank\n---\n")
        (root / "_data" / "orcid.yaml").write_text("- orcid: legacy-must-not-be-read\n")
        (root / "_data" / "sources.yaml").write_text(
            '- id: doi:10.1234/shared\n  title: Manual title\n'
        )
        response = {"group": [{"work-summary": [{"external-ids": {
            "external-id": [{"external-id-relationship": "self",
                             "external-id-type": "doi",
                             "external-id-value": "10.1234/shared"}]
        }}]}]}
        script = Path(__file__).resolve().parents[1] / "cite.py"
        original_cwd = Path.cwd()
        try:
            os.chdir(root)
            import util
            with patch("urllib.request.urlopen", return_value=io.BytesIO(
                json.dumps(response).encode()
            )) as query, patch.object(util, "cite_with_manubot", return_value={
                "id": "doi:10.1234/shared", "title": "API title", "authors": ["Author"]
            }), patch("builtins.print"):
                runpy.run_path(str(script), run_name="__main__")
            self.assertEqual(query.call_count, 1)
            self.assertIn("0000-0002-1825-0097/works", query.call_args.args[0].full_url)
            result = yaml.safe_load((root / "_data" / "citations.yaml").read_text())
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["title"], "Manual title")
            self.assertEqual(result[0]["authors"], ["Author"])
            self.assertEqual(result[0]["orcids"], ["0000-0002-1825-0097"])
            self.assertNotIn("name", result[0])
            self.assertNotIn("image", result[0])
        finally:
            os.chdir(original_cwd)

    def test_preview_watches_members_without_watching_generated_citations(self):
        from watchdog.utils.patterns import match_any_paths
        entrypoint = Path(__file__).resolve().parents[2] / ".docker" / "entrypoint.sh"
        pattern_line = next(line for line in entrypoint.read_text().splitlines()
                            if '--patterns="*/_data/sources' in line)
        patterns = pattern_line.split('"')[1].split(";")
        for filename in ("_members/new.md", "/usr/src/app/_members/new.md",
                         "_data/sources.yaml", "/usr/src/app/_data/sources.yaml"):
            self.assertTrue(match_any_paths([filename], included_patterns=patterns))
        self.assertFalse(match_any_paths(["_data/citations.yaml"], included_patterns=patterns))

    def test_pr_snapshot_keeps_member_and_data_directories(self):
        workflow = Path(__file__).resolve().parents[2] / ".github/workflows/get-sources.yaml"
        steps = yaml.safe_load(workflow.read_text())["jobs"]["get-sources"]["steps"]
        command = next(step["run"] for step in steps
                       if step.get("name") == "Prepare citation inputs")
        script = command.split("python - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        root = Path(self.directory.name)
        (root / "_members").mkdir()
        (root / "_data").mkdir()
        (root / "_members" / "one.md").write_text("---\nname: Test\n---\n")
        (root / "_data" / "sources.yaml").write_text("[]\n")
        (root / "untrusted.py").write_text("raise RuntimeError('must not run')\n")
        original_cwd = Path.cwd()
        try:
            os.chdir(root)
            with patch.dict(os.environ, {"RUNNER_TEMP": str(root / "runner-temp")}):
                exec(compile(script, str(workflow), "exec"), {})
            snapshot = root / "runner-temp" / "citation-inputs"
            self.assertTrue((snapshot / "_members" / "one.md").is_file())
            self.assertTrue((snapshot / "_data" / "sources.yaml").is_file())
            self.assertFalse((snapshot / "untrusted.py").exists())
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
