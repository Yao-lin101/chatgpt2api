import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

os.environ.setdefault("CHATGPT2API_AUTH_KEY", "test-auth")

for mod in [
    "fastapi", "fastapi.concurrency", "fastapi.responses",
    "sqlalchemy", "sqlalchemy.ext", "sqlalchemy.ext.declarative", "sqlalchemy.orm",
    "curl_cffi", "curl_cffi.requests", "tiktoken", "git", "git.exc", "PIL", "PIL.Image",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from services.log_service import LogService


class LogServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = Path(self.temp_dir.name) / "logs.jsonl"
        self.service = LogService(self.log_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_clear_all_logs(self) -> None:
        self.service.add("call", "call log 1")
        self.service.add("call", "call log 2")
        self.service.add("account", "account log 1")

        self.assertEqual(len(self.service.list()), 3)
        res = self.service.clear()
        self.assertEqual(res["removed"], 3)
        self.assertEqual(len(self.service.list()), 0)

    def test_clear_by_type(self) -> None:
        self.service.add("call", "call log 1")
        self.service.add("call", "call log 2")
        self.service.add("account", "account log 1")

        # Clear only call logs
        res = self.service.clear(type="call")
        self.assertEqual(res["removed"], 2)

        remaining = self.service.list()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["type"], "account")

        # Clear account logs
        res2 = self.service.clear(type="account")
        self.assertEqual(res2["removed"], 1)
        self.assertEqual(len(self.service.list()), 0)


if __name__ == "__main__":
    unittest.main()
