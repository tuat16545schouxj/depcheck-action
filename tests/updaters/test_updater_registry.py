import unittest
from unittest.mock import patch, MagicMock

from src.updaters.registry import get_all_updaters, updater_for_file, apply_updates
from src.detectors.base import Dependency


def _dep(name, current="1.0.0", latest="2.0.0", outdated=True, ecosystem="python"):
    return Dependency(
        name=name,
        current_version=current,
        latest_version=latest,
        ecosystem=ecosystem,
        outdated=outdated,
    )


class TestUpdaterRegistry(unittest.TestCase):

    def test_get_all_updaters_returns_list(self):
        updaters = get_all_updaters()
        self.assertIsInstance(updaters, list)
        self.assertGreater(len(updaters), 0)

    def test_get_all_updaters_have_supports_method(self):
        for updater in get_all_updaters():
            self.assertTrue(callable(getattr(updater, "supports", None)))

    def test_updater_for_requirements_txt(self):
        updater = updater_for_file("requirements.txt")
        self.assertIsNotNone(updater)

    def test_updater_for_package_json(self):
        updater = updater_for_file("package.json")
        self.assertIsNotNone(updater)

    def test_updater_for_cargo_toml(self):
        updater = updater_for_file("Cargo.toml")
        self.assertIsNotNone(updater)
        from src.updaters.rust_updater import RustUpdater
        self.assertIsInstance(updater, RustUpdater)

    def test_updater_for_unknown_file_returns_none(self):
        updater = updater_for_file("unknown.xyz")
        self.assertIsNone(updater)

    def test_apply_updates_calls_updater(self):
        mock_updater = MagicMock()
        mock_updater.supports.return_value = True
        mock_summary = MagicMock()
        mock_updater.update.return_value = mock_summary

        deps = [_dep("requests")]
        file_deps = {"requirements.txt": deps}

        with patch("src.updaters.registry.get_all_updaters", return_value=[mock_updater]):
            summaries = apply_updates(file_deps)

        mock_updater.update.assert_called_once_with("requirements.txt", deps)
        self.assertIn("requirements.txt", summaries)

    def test_apply_updates_skips_unsupported(self):
        mock_updater = MagicMock()
        mock_updater.supports.return_value = False

        file_deps = {"unknown.xyz": [_dep("something")]}

        with patch("src.updaters.registry.get_all_updaters", return_value=[mock_updater]):
            summaries = apply_updates(file_deps)

        mock_updater.update.assert_not_called()
        self.assertEqual(summaries, {})
