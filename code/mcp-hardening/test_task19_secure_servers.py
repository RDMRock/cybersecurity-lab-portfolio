"""Security regression checks for the Task 19 FastMCP replacements."""

import asyncio
import subprocess
import unittest
from unittest.mock import patch

# Portfolio adaptation: isolate tests from original course databases.
import os
import sqlite3
import tempfile
from pathlib import Path

_fixture = tempfile.TemporaryDirectory(prefix="mcp-portfolio-test-")
_fixture_root = Path(_fixture.name)
(_fixture_root / "data/public").mkdir(parents=True)
(_fixture_root / "data/public/note.txt").write_text("This is intentionally public test data.\n")
with sqlite3.connect(_fixture_root / "mcp_lab_vulnerable.db") as _db:
    _db.execute("CREATE TABLE users (id INTEGER, username TEXT, role TEXT)")
    _db.executemany("INSERT INTO users VALUES (?, ?, ?)", [
        (1, "admin", "admin"), (2, "alice", "user"), (3, "bob", "user")
    ])
_old_root = os.environ.get("MCP_LAB_ROOT")
os.environ["MCP_LAB_ROOT"] = str(_fixture_root)
import task19_secure_servers as secure
if _old_root is None:
    os.environ.pop("MCP_LAB_ROOT", None)
else:
    os.environ["MCP_LAB_ROOT"] = _old_root

def tearDownModule():
    _fixture.cleanup()



class SecureDatabaseTests(unittest.TestCase):
    def test_sql_injection_does_not_return_users(self):
        result = secure.query_users_secure("' OR '1'='1")
        self.assertTrue(result["success"])
        self.assertEqual(result["row_count"], 0)

    def test_normal_lookup_preserves_public_fields_only(self):
        result = secure.query_users_secure("admin")
        self.assertEqual(result["row_count"], 1)
        self.assertEqual(result["results"][0]["username"], "admin")
        self.assertEqual(set(result["results"][0]), {"id", "username", "role"})

    def test_search_treats_wildcards_as_literal(self):
        self.assertEqual(secure.search_users_secure("%")["count"], 0)
        self.assertEqual(secure.search_users_secure("adm")["count"], 1)


class SecureGitTests(unittest.TestCase):
    @patch.object(secure.subprocess, "run")
    def test_shell_payload_rejected_before_process(self, runner):
        result = secure.git_clone_secure("unused; printf 'uid='; id -u; #")
        self.assertFalse(result["success"])
        runner.assert_not_called()

    @patch.object(secure.subprocess, "run")
    def test_valid_clone_uses_argument_list_without_shell(self, runner):
        runner.return_value = subprocess.CompletedProcess([], 0, "", "")
        result = secure.git_clone_secure("https://github.com/sfucybersecurity/cmpt782.git")
        self.assertTrue(result["success"])
        args, kwargs = runner.call_args
        self.assertEqual(args[0][:4], ["git", "clone", "--", "https://github.com/sfucybersecurity/cmpt782.git"])
        self.assertIs(kwargs["shell"], False)


class SecureFileTests(unittest.TestCase):
    def test_path_traversal_rejected(self):
        result = secure.read_file_secure("data/public/../private/secret.txt")
        self.assertFalse(result["success"])

    def test_normal_public_read_works(self):
        result = secure.read_file_secure("note.txt")
        self.assertTrue(result["success"])
        self.assertIn("intentionally public", result["content"])

    @patch.object(secure.requests, "get")
    def test_private_url_rejected_before_request(self, get):
        result = secure.fetch_url_secure("http://169.254.169.254/latest/meta-data/")
        self.assertFalse(result["success"])
        get.assert_not_called()


class FastMCPRegistrationTests(unittest.TestCase):
    def test_all_three_servers_register_their_tools(self):
        expected = {
            secure.git_mcp: {"git_clone", "git_diff", "git_log"},
            secure.file_mcp: {"read_file", "write_file", "list_directory", "fetch_url"},
            secure.db_mcp: {"query_users", "search_users"},
        }
        for server, names in expected.items():
            with self.subTest(server=server.name):
                self.assertEqual({tool.name for tool in asyncio.run(server.list_tools())}, names)

    def test_original_attack_payloads_fail_through_fastmcp(self):
        cases = [
            (secure.db_mcp, "query_users", {"username": "' OR '1'='1"}),
            (secure.git_mcp, "git_clone", {"repo_url": "unused; printf 'uid='; id -u; #"}),
            (secure.file_mcp, "read_file", {"filepath": "data/public/../private/secret.txt"}),
        ]
        for server, tool, params in cases:
            with self.subTest(tool=tool):
                result = asyncio.run(server.call_tool(tool, params)).structured_content
                if tool == "query_users":
                    self.assertEqual(result["row_count"], 0)
                else:
                    self.assertFalse(result["success"])
                self.assertNotIn("admin_pass_2025", str(result))
                self.assertNotIn("LAB_PRIVATE_MARKER", str(result))
                self.assertNotIn("uid=", str(result))


if __name__ == "__main__":
    unittest.main()
