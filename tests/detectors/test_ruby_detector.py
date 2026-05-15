import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.detectors.ruby_detector import RubyDetector


GEMFILE_LOCK_CONTENT = """
GEM
  remote: https://rubygems.org/
  specs:
    rails (7.0.4)
    rack (2.2.4)

BUNDLED WITH
   2.3.26
"""

GEMFILE_CONTENT = """
source 'https://rubygems.org'

gem 'rails', '7.0.4'
gem 'rack'
"""


class TestRubyDetector(unittest.TestCase):
    def setUp(self):
        self.detector = RubyDetector()
        self.tmpdir = tempfile.mkdtemp()

    def _write_temp(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_supports_gemfile_lock(self):
        self.assertTrue(self.detector.supports("Gemfile.lock"))

    def test_supports_gemfile(self):
        self.assertTrue(self.detector.supports("Gemfile"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports("requirements.txt"))
        self.assertFalse(self.detector.supports("package.json"))

    @patch("src.detectors.ruby_detector.RubyDetector._fetch_latest")
    def test_detect_gemfile_lock(self, mock_fetch):
        mock_fetch.side_effect = lambda name: "8.0.0" if name == "rails" else "2.2.4"
        path = self._write_temp("Gemfile.lock", GEMFILE_LOCK_CONTENT)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "ruby")
        self.assertEqual(len(result.dependencies), 2)
        self.assertEqual(len(result.outdated), 1)
        self.assertEqual(result.outdated[0].name, "rails")
        self.assertEqual(result.outdated[0].latest_version, "8.0.0")

    @patch("src.detectors.ruby_detector.RubyDetector._fetch_latest")
    def test_detect_gemfile(self, mock_fetch):
        mock_fetch.return_value = None
        path = self._write_temp("Gemfile", GEMFILE_CONTENT)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "ruby")
        self.assertEqual(len(result.dependencies), 2)
        self.assertEqual(len(result.outdated), 0)

    @patch("src.detectors.ruby_detector.requests.get")
    def test_fetch_latest_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"version": "7.1.0"}
        mock_get.return_value = mock_resp
        result = self.detector._fetch_latest("rails")
        self.assertEqual(result, "7.1.0")

    @patch("src.detectors.ruby_detector.requests.get")
    def test_fetch_latest_failure(self, mock_get):
        mock_get.side_effect = Exception("network error")
        result = self.detector._fetch_latest("rails")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
