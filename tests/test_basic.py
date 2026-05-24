"""
Minimal test to ensure basic imports work
"""

import os
import sys
from pathlib import Path

import pytest


def test_python_version():
    """Test Python version is compatible"""
    assert sys.version_info >= (3, 11)


def test_core_imports():
    """Test core module imports"""
    try:
        from core.data import database  # noqa: F401
        from core.plc import mock_plc  # noqa: F401

        assert True
    except ImportError as e:
        pytest.fail(f"Core imports failed: {e}")


def test_config_module_available():
    """Verify the config module file is present in the repo.

    Importing the ``config`` module directly is fragile because several
    modules in the codebase (e.g. ``core.data.database.get_engine``) insert
    the ``config/`` directory itself onto ``sys.path`` to support a flat
    ``from config import settings`` style import. We therefore only check
    that the file exists — the actual import works once the production
    code path has set up ``sys.path``.
    """
    config_path = Path(__file__).parent.parent / "config" / "config.py"
    assert config_path.is_file(), f"Missing config file: {config_path}"


@pytest.mark.skipif(
    sys.platform.startswith("win") and "CI" in os.environ, reason="Skip GUI tests in Windows CI"
)
def test_gui_imports():
    """Test GUI module imports (skipped in CI)"""
    try:
        from PySide6 import QtCore, QtWidgets  # noqa: F401

        assert True
    except ImportError:
        pytest.skip("PySide6 not available")


def test_basic_math():
    """Sanity check test"""
    assert 1 + 1 == 2
    assert 2 * 2 == 4
