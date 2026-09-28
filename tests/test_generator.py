from __future__ import annotations
import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from tests.common import ROOT
from central_repo_scaffold.config import load_config
from central_repo_scaffold.errors import GenerationError
from central_repo_scaffold.generator import expected_files, render_repository

class GeneratorTest(unittest.TestCase):
    def setUp(self): self.config = load_config(ROOT / "examples/domain.yaml")
    def test_renders_complete_deterministic_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp)/"first", Path(tmp)/"second"
            render_repository(self.config, first); render_repository(self.config, second)
            for relative in expected_files(): self.assertTrue((first/relative).exists(), relative)
            self.assertEqual(snapshot(first), snapshot(second))
            agents=(first/"AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("只读", agents); self.assertIn("可修改", agents)
            self.assertTrue(os.access(first/"scripts/dev-worktree.py", os.X_OK))
            corpus=snapshot(first).decode("utf-8", errors="ignore")
            for forbidden in ("search_central_incentive_repo","tradeflow-lab","/Users/bytedance","~/workspace"):
                self.assertNotIn(forbidden, corpus)
            manifest=(first/"docs/build-record/07-generated-files.md").read_text(encoding="utf-8")
            for relative in expected_files():
                self.assertIn(f"`{relative}`",manifest)
    def test_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"exists"; output.mkdir()
            with self.assertRaises(GenerationError): render_repository(self.config, output)
    def test_undefined_template_variable_fails_and_cleans_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            templates=Path(tmp)/"templates"; templates.mkdir()
            (templates/"README.md.j2").write_text("{{ missing_value }}",encoding="utf-8")
            output=Path(tmp)/"output"
            with patch("central_repo_scaffold.generator._template_root",return_value=templates):
                with self.assertRaises(GenerationError):
                    render_repository(self.config,output)
            self.assertFalse(output.exists())
def snapshot(root):
    chunks=[]
    for p in sorted(p for p in root.rglob("*") if p.is_file()): chunks += [str(p.relative_to(root)).encode(),b"\0",p.read_bytes(),b"\0"]
    return b"".join(chunks)
if __name__ == "__main__": unittest.main()
