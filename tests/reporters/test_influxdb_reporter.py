"""Tests for InfluxDBReporter."""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.detectors.base import Dependency, DetectionResult
from src.reporters.influxdb_reporter import InfluxDBReporter

_FIXED_TS = 1_700_000_000_000_000_000  # fixed nanosecond timestamp


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest)


def _make_result(ecosystem: str, deps) -> DetectionResult:
    return DetectionResult(ecosystem=ecosystem, dependencies=deps, source_file="x")


class TestInfluxDBReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.reporter = InfluxDBReporter(timestamp=_FIXED_TS)

    # ------------------------------------------------------------------
    # Render output format
    # ------------------------------------------------------------------

    def test_render_returns_string(self):
        result = _make_result("python", [_dep("requests", "2.28.0", "2.31.0")])
        output = self.reporter.render([result])
        self.assertIsInstance(output, str)

    def test_render_contains_measurement_name(self):
        result = _make_result("python", [_dep("flask", "2.0.0", "2.3.0")])
        output = self.reporter.render([result])
        self.assertIn("depcheck,", output)

    def test_render_contains_ecosystem_tag(self):
        result = _make_result("node", [_dep("lodash", "4.17.0", "4.17.21")])
        output = self.reporter.render([result])
        self.assertIn("ecosystem=node", output)

    def test_render_counts_total(self):
        deps = [_dep("a", "1.0", "2.0"), _dep("b", "1.0", "1.0")]
        result = _make_result("python", deps)
        output = self.reporter.render([result])
        self.assertIn("total=2i", output)

    def test_render_counts_outdated(self):
        deps = [_dep("a", "1.0", "2.0"), _dep("b", "1.0", "1.0")]
        result = _make_result("python", deps)
        output = self.reporter.render([result])
        self.assertIn("outdated=1i", output)

    def test_render_counts_up_to_date(self):
        deps = [_dep("a", "1.0", "2.0"), _dep("b", "1.0", "1.0")]
        result = _make_result("python", deps)
        output = self.reporter.render([result])
        self.assertIn("up_to_date=1i", output)

    def test_render_includes_timestamp(self):
        result = _make_result("rust", [_dep("serde", "1.0.0", "1.0.1")])
        output = self.reporter.render([result])
        self.assertIn(str(_FIXED_TS), output)

    def test_multiple_results_produce_multiple_lines(self):
        r1 = _make_result("python", [_dep("a", "1", "2")])
        r2 = _make_result("node", [_dep("b", "1", "1")])
        output = self.reporter.render([r1, r2])
        lines = output.strip().splitlines()
        self.assertEqual(len(lines), 2)

    def test_ecosystem_spaces_escaped(self):
        result = _make_result("my ecosystem", [_dep("x", "1", "2")])
        output = self.reporter.render([result])
        self.assertIn("ecosystem=my\\ ecosystem", output)

    # ------------------------------------------------------------------
    # HTTP send path
    # ------------------------------------------------------------------

    def test_no_send_when_url_absent(self):
        """render() must NOT attempt HTTP when url is None."""
        with patch("src.reporters.influxdb_reporter._urllib") as mock_urllib:
            reporter = InfluxDBReporter(token="tok", timestamp=_FIXED_TS)
            reporter.render([_make_result("go", [])])
            mock_urllib.Request.assert_not_called()

    def test_send_called_when_url_and_token_present(self):
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.status = 204

        with patch("src.reporters.influxdb_reporter._urllib") as mock_urllib:
            mock_urllib.Request.return_value = MagicMock()
            mock_urllib.urlopen.return_value = mock_resp

            reporter = InfluxDBReporter(
                url="http://localhost:8086",
                token="mytoken",
                timestamp=_FIXED_TS,
            )
            reporter.render([_make_result("python", [_dep("pip", "23", "24")])])
            mock_urllib.Request.assert_called_once()
            call_kwargs = mock_urllib.Request.call_args
            self.assertIn("/api/v2/write", call_kwargs[0][0])
