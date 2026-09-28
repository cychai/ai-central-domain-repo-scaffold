from __future__ import annotations
import os,shutil,subprocess,tempfile,time,unittest
from pathlib import Path
from tests.common import ROOT,run_cli
class GeneratedWorktreeTest(unittest.TestCase):
    def test_mount_modes_selectors_no_head_and_requirement_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"): make_repo(sources/name, committed=name!="inventory-query")
            config=(ROOT/"examples/domain.yaml").read_text(encoding="utf-8")
            for name in ("order-api","inventory-query","billing-ledger"): config=config.replace(f"local_path: ~/workspace/example/{name}",f"local_path: {sources/name}")
            cp=base/"domain.yaml"; cp.write_text(config,encoding="utf-8"); output=base/"central"
            created=run_cli("create","--config",str(cp),"--output",str(output)); self.assertEqual(created.returncode,0,created.stderr)
            env={f"CENTRAL_SERVICE_{name.replace('-', '_').upper()}_PATH":str(sources/name) for name in ("order-api","inventory-query","billing-ledger")}
            switch_to_feature_branch(output)
            result=manager(output,"init","--services","inventory-query",env=env); self.assertEqual(result.returncode,0,result.stderr); self.assertTrue((output/"services/example/inventory-query").is_symlink())
            result=manager(output,"init","--services","services/example/billing-ledger",env=env); self.assertEqual(result.returncode,0,result.stderr); self.assertTrue((output/"services/example/billing-ledger/README.md").is_file()); self.assertFalse((output/"services/example/billing-ledger/.git").exists())
            result=manager(output,"init","--services","order-api",env=env); self.assertEqual(result.returncode,0,result.stderr); self.assertEqual(git(output/"services/example/order-api","rev-parse","--is-inside-work-tree"),"true")
            result=manager(output,"create","feat/training"); self.assertEqual(result.returncode,0,result.stderr); requirement=Path(result.stdout.strip().splitlines()[-1]); self.assertTrue(requirement.is_dir())
            result=manager(output,"remove","feat/training"); self.assertEqual(result.returncode,0,result.stderr); self.assertFalse(requirement.exists())
            cleanup_mounts(output,sources)
    def test_all_selector_initializes_every_service_after_complete_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"):
                make_repo(sources/name, committed=True)
            output=create_with_sources(base,sources)
            switch_to_feature_branch(output)
            env=service_env(sources)
            result=manager(output,"init","--services","all",env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((output/"services/example/order-api").is_dir())
            self.assertTrue((output/"services/example/inventory-query").is_symlink())
            self.assertTrue((output/"services/example/billing-ledger/README.md").is_file())
            cleanup_mounts(output,sources)
    def test_preflight_failure_preserves_existing_path_and_creates_nothing_else(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"):
                make_repo(sources/name, committed=True)
            output=create_with_sources(base,sources)
            switch_to_feature_branch(output)
            existing=output/"services/example/inventory-query"
            existing.mkdir(parents=True)
            marker=existing/"keep.txt"; marker.write_text("keep",encoding="utf-8")
            result=manager(output,"init","--services","all",env=service_env(sources))
            self.assertNotEqual(result.returncode,0)
            self.assertTrue(marker.is_file())
            self.assertFalse((output/"services/example/order-api").exists())
            self.assertFalse((output/"services/example/billing-ledger").exists())
    def test_runtime_failure_rolls_back_mounts_created_by_current_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"):
                make_repo(sources/name, committed=True)
            text=(ROOT/"examples/domain.yaml").read_text(encoding="utf-8")
            blocks=text.split("  - id: ")
            header=blocks[0]
            service_blocks={"order-api":blocks[1],"inventory-query":blocks[2],"billing-ledger":blocks[3]}
            reordered=header+"  - id: inventory-query"+service_blocks["inventory-query"]
            reordered+="  - id: order-api"+service_blocks["order-api"]
            reordered+="  - id: billing-ledger"+service_blocks["billing-ledger"]
            config=base/"domain.yaml"; config.write_text(reordered,encoding="utf-8")
            output=base/"central"
            created=run_cli("create","--config",str(config),"--output",str(output))
            self.assertEqual(created.returncode,0,created.stderr)
            switch_to_feature_branch(output)
            # Occupy the exact service-worktree branch after preflight but before add.
            subprocess.run(
                ["git","-C",str(sources/"order-api"),"branch","central/feat-services-order-api"],
                check=True,
            )
            result=manager(
                output,
                "init",
                "--services","inventory-query,order-api",
                env=service_env(sources),
            )
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((output/"services/example/inventory-query").exists())
            self.assertFalse((output/"services/example/order-api").exists())
    def test_worktree_mode_rejects_source_without_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"source"; make_repo(source,False)
            text=(ROOT/"examples/domain.yaml").read_text(encoding="utf-8").replace("local_path: ~/workspace/example/order-api",f"local_path: {source}")
            cp=Path(tmp)/"domain.yaml"; cp.write_text(text,encoding="utf-8"); output=Path(tmp)/"central"
            self.assertEqual(run_cli("create","--config",str(cp),"--output",str(output)).returncode,0)
            switch_to_feature_branch(output)
            result=manager(output,"init","--services","order-api",env={"CENTRAL_SERVICE_ORDER_API_PATH":str(source)}); self.assertNotEqual(result.returncode,0); self.assertIn("committed HEAD",result.stderr); self.assertFalse((output/"services/example/order-api").exists())
            remove_tree_with_retry(source/".git")
    def test_worktree_mode_uses_declared_default_branch_as_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"):
                make_repo(sources/name, committed=True)
            source=sources/"order-api"
            main_head=git(source,"rev-parse","main")
            subprocess.run(
                ["git","-C",str(source),"switch","-c","unrelated"],
                check=True,
                capture_output=True,
            )
            (source/"unrelated.txt").write_text("different base",encoding="utf-8")
            subprocess.run(["git","-C",str(source),"add","."],check=True)
            subprocess.run(
                ["git","-C",str(source),"-c","user.name=Test","-c","user.email=test@example.com","commit","-m","unrelated"],
                check=True,
                capture_output=True,
            )
            output=create_with_sources(base,sources)
            switch_to_feature_branch(output)
            result=manager(
                output,
                "init",
                "--services","order-api",
                env=service_env(sources),
            )
            self.assertEqual(result.returncode,0,result.stderr)
            mounted=output/"services/example/order-api"
            self.assertEqual(git(mounted,"rev-parse","HEAD"),main_head)
            subprocess.run(
                ["git","-C",str(source),"worktree","remove","--force",str(mounted)],
                check=True,
                capture_output=True,
            )
    def test_default_branch_rejects_service_initialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"):
                make_repo(sources/name, committed=True)
            output=create_with_sources(base,sources)
            result=manager(
                output,
                "init",
                "--services","inventory-query",
                env=service_env(sources),
            )
            self.assertNotEqual(result.returncode,0)
            self.assertIn("默认分支",result.stderr)
            self.assertFalse((output/"services/example/inventory-query").exists())
    def test_unknown_service_selector_is_rejected_without_creating_mounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); sources=base/"sources"; sources.mkdir()
            for name in ("order-api","inventory-query","billing-ledger"):
                make_repo(sources/name, committed=True)
            output=create_with_sources(base,sources)
            switch_to_feature_branch(output)
            result=manager(
                output,
                "init",
                "--services","missing-service",
                env=service_env(sources),
            )
            self.assertNotEqual(result.returncode,0)
            self.assertIn("无法唯一解析",result.stderr)
            self.assertFalse((output/"services/example/order-api").exists())
def make_repo(path,committed):
    path.mkdir(); subprocess.run(["git","init","-b","main",str(path)],check=True,capture_output=True); (path/"README.md").write_text(path.name,encoding="utf-8")
    if committed:
        subprocess.run(["git","-C",str(path),"add","."],check=True); subprocess.run(["git","-C",str(path),"-c","user.name=Test","-c","user.email=test@example.com","commit","-m","init"],check=True,capture_output=True)
def create_with_sources(base,sources):
    text=(ROOT/"examples/domain.yaml").read_text(encoding="utf-8")
    for name in ("order-api","inventory-query","billing-ledger"):
        text=text.replace(f"local_path: ~/workspace/example/{name}",f"local_path: {sources/name}")
    config=base/"domain.yaml"; config.write_text(text,encoding="utf-8")
    output=base/"central"
    result=run_cli("create","--config",str(config),"--output",str(output))
    if result.returncode:
        raise AssertionError(result.stderr)
    return output
def service_env(sources):
    return {f"CENTRAL_SERVICE_{name.replace('-', '_').upper()}_PATH":str(sources/name) for name in ("order-api","inventory-query","billing-ledger")}
def switch_to_feature_branch(output):
    subprocess.run(
        ["git","-C",str(output),"switch","-c","feat/services"],
        check=True,
        capture_output=True,
    )
def cleanup_mounts(output,sources):
    order=output/"services/example/order-api"
    subprocess.run(
        ["git","-C",str(sources/"order-api"),"worktree","remove","--force",str(order)],
        check=True,
        capture_output=True,
    )
    inventory=output/"services/example/inventory-query"
    inventory.unlink()
    shutil.rmtree(output/"services/example/billing-ledger")
def remove_tree_with_retry(path):
    for attempt in range(5):
        try:
            shutil.rmtree(path)
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.05 * (attempt + 1))
def manager(root,*args,env=None):
    merged=os.environ.copy()
    if env: merged.update(env)
    return subprocess.run(["python3","scripts/dev-worktree.py",*args],cwd=root,text=True,capture_output=True,env=merged)
def git(root,*args): return subprocess.run(["git","-C",str(root),*args],check=True,text=True,capture_output=True).stdout.strip()
if __name__ == "__main__": unittest.main()
