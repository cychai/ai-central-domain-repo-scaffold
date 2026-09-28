from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from tests.common import ROOT
from central_repo_scaffold.config import load_config
from central_repo_scaffold.errors import ConfigError

class ConfigTest(unittest.TestCase):
    def test_valid_multi_service_config_is_normalized_and_redacted(self):
        config = load_config(ROOT / "examples/domain.yaml")
        self.assertEqual(config.domain.repository, "order-fulfillment-central-domain")
        self.assertEqual(len(config.services), 3)
        self.assertEqual({s.access for s in config.services}, {"read-write", "read-only"})
        self.assertNotIn("local_path", str(config.public_dict()))
    def test_rejects_duplicate_service_id_with_precise_path(self):
        self.assert_invalid("  - id: inventory-query", "services[1].id", "  - id: order-api")
    def test_rejects_unsafe_mount_path(self):
        self.assert_invalid("mount_path: services/example/order-api", "services[0].mount_path", "mount_path: ../escape")
    def test_rejects_empty_verification_command(self):
        self.assert_invalid("      - go test ./...", "services[0].verification[0]", "      - '   '")
    def test_rejects_verification_command_with_newline(self):
        self.assert_invalid(
            "      - go test ./...",
            "services[0].verification[0]",
            "      - |-\n          go test ./...\n          echo injected",
        )
    def test_rejects_invalid_access_enum(self):
        self.assert_invalid(
            "access: read-write",
            "services[0].access",
            "access: owner-only",
        )
    def test_rejects_invalid_fetch_mode_enum(self):
        self.assert_invalid(
            "fetch_mode: worktree",
            "services[0].fetch_mode",
            "fetch_mode: clone",
        )
    def test_rejects_unknown_fields(self):
        self.assert_invalid("schema_version: 1", "unexpected", "schema_version: 1\nunexpected: true")
    def test_rejects_unknown_directory_template_variable(self):
        self.assert_invalid("{repository}__{branch_slug}", "worktree.directory_template", "{repository}__{unknown}")
    def test_rejects_repository_name_that_can_escape_worktree_root(self):
        self.assert_invalid(
            "repository: order-fulfillment-central-domain",
            "domain.repository",
            "repository: ../../escaped",
        )
    def test_rejects_directory_template_with_path_separator(self):
        self.assert_invalid(
            '"{repository}__{branch_slug}"',
            "worktree.directory_template",
            '"../{repository}__{branch_slug}"',
        )
    def assert_invalid(self, needle, expected, replacement):
        text = (ROOT / "examples/domain.yaml").read_text(encoding="utf-8").replace(needle, replacement, 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.yaml"; path.write_text(text, encoding="utf-8")
            with self.assertRaises(ConfigError) as error: load_config(path)
            self.assertIn(expected, str(error.exception))
if __name__ == "__main__": unittest.main()
