from __future__ import annotations
import subprocess, tempfile, unittest
from pathlib import Path
from tests.common import ROOT, run_cli
class CliTest(unittest.TestCase):
    def test_read_only_stages_do_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"repo"
            for command in ("inspect","validate","plan"):
                args=[command,"--config",str(ROOT/"examples/domain.yaml")]
                if command=="plan": args += ["--output",str(output)]
                result=run_cli(*args); self.assertEqual(result.returncode,0,result.stderr); self.assertFalse(output.exists())
    def test_render_then_git_init_creates_one_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"repo"
            result=run_cli("render","--config",str(ROOT/"examples/domain.yaml"),"--output",str(output)); self.assertEqual(result.returncode,0,result.stderr); self.assertFalse((output/".git").exists())
            result=run_cli("git-init","--output",str(output)); self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(git(output,"rev-list","--count","HEAD"),"1"); self.assertEqual(git(output,"branch","--show-current"),"main")
    def test_git_init_rejects_incomplete_render_before_creating_git_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"repo"
            result=run_cli("render","--config",str(ROOT/"examples/domain.yaml"),"--output",str(output))
            self.assertEqual(result.returncode,0,result.stderr)
            (output/"AGENTS.md").unlink()
            result=run_cli("git-init","--output",str(output))
            self.assertNotEqual(result.returncode,0)
            self.assertIn("缺少生成文件",result.stderr)
            self.assertFalse((output/".git").exists())
    def test_create_is_transactional_and_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"repo"; result=run_cli("create","--config",str(ROOT/"examples/domain.yaml"),"--output",str(output))
            self.assertEqual(result.returncode,0,result.stderr); self.assertEqual(git(output,"rev-list","--count","HEAD"),"1")
            verify=subprocess.run(["make","verify"],cwd=output,text=True,capture_output=True); self.assertEqual(verify.returncode,0,verify.stderr)
    def test_create_fails_without_git_identity_and_cleans_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)/"home"; home.mkdir(); output=Path(tmp)/"repo"
            result=run_cli("create","--config",str(ROOT/"examples/domain.yaml"),"--output",str(output),env={"HOME":str(home),"GIT_CONFIG_NOSYSTEM":"1"})
            self.assertNotEqual(result.returncode,0); self.assertIn("Git 身份",result.stderr); self.assertFalse(output.exists())
    def test_keep_failed_output_preserves_diagnostic_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)/"home"; home.mkdir(); output=Path(tmp)/"repo"
            result=run_cli(
                "create",
                "--config",str(ROOT/"examples/domain.yaml"),
                "--output",str(output),
                "--keep-failed-output",
                env={"HOME":str(home),"GIT_CONFIG_NOSYSTEM":"1"},
            )
            failed=Path(tmp)/".repo.failed-output"
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(output.exists())
            self.assertTrue((failed/"AGENTS.md").is_file())
            self.assertFalse((failed/".git").exists())
def git(root,*args): return subprocess.run(["git","-C",str(root),*args],check=True,text=True,capture_output=True).stdout.strip()
if __name__ == "__main__": unittest.main()
