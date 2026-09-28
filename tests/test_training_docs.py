from __future__ import annotations
import re,unittest
from tests.common import ROOT
from central_repo_scaffold.generator import expected_files
class TrainingDocsTest(unittest.TestCase):
    def test_training_inventory_and_chapter_contract(self):
        sections=["本节目标","前置输入","为什么要做","操作步骤","关键文件解析","设计取舍","验证命令与预期结果","常见错误及根因","学员练习","完成标准"]
        files=sorted((ROOT/"docs").glob("[0-1][0-9]-*.md")); self.assertEqual(len(files),13)
        for path in files:
            text=path.read_text(encoding="utf-8")
            for section in sections: self.assertIn(f"## {section}",text,f"{path.name}: {section}")
    def test_docs_reference_real_cli_and_status_contract(self):
        corpus="\n".join(p.read_text(encoding="utf-8") for p in (ROOT/"docs").glob("*.md"))
        for command in ("inspect","validate","plan","render","git-init","verify","create"): self.assertRegex(corpus,rf"central_repo_scaffold {re.escape(command)}")
        for status in ("confirmed","inferred","manual_required","not-executed","failed","passed"): self.assertIn(status,corpus)
    def test_readme_makefile_and_expected_tree_are_aligned(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8"); makefile=(ROOT/"Makefile").read_text(encoding="utf-8")
        for target in ("install","test","verify","example"): self.assertIn(f"make {target}",readme); self.assertRegex(makefile,rf"(?m)^{target}:")
        self.assertIn("BOOTSTRAP_PYTHON",readme)
        self.assertIn("BOOTSTRAP_PYTHON",makefile)
        tree=(ROOT/"examples/expected-tree.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(tree, list(expected_files()))
        self.assertIn("AGENTS.md",tree); self.assertIn("docs/build-record/08-verification-report.md",tree)
        self.assertIn("scripts/verify-scaffold.py", makefile)
if __name__ == "__main__": unittest.main()
