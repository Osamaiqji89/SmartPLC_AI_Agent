"""
Minimal test to ensure basic imports work
"""

import sys
import pytest


def test_python_version():
    """Test Python version is compatible"""
    assert sys.version_info >= (3, 10)


def test_core_imports():
    """Test core module imports"""
    try:
        from core.plc import mock_plc
        from core.data import database

        assert True
    except ImportError as e:
        pytest.fail(f"Core imports failed: {e}")


def test_config_import():
    """Test config module import"""
    try:
        from config import config

        assert True
    except ImportError as e:
        pytest.fail(f"Config import failed: {e}")


@pytest.mark.skipif(
    sys.platform.startswith("win") and "CI" in sys.environ, reason="Skip GUI tests in Windows CI"
)
def test_gui_imports():
    """Test GUI module imports (skipped in CI)"""
    try:
        from PySide6 import QtCore, QtWidgets

        assert True
    except ImportError:
        pytest.skip("PySide6 not available")


def test_basic_math():
    """Sanity check test"""
    assert 1 + 1 == 2
    assert 2 * 2 == 4
