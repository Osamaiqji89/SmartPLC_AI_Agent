"""
Theme Manager
Handles loading and switching between Light/Dark themes
"""

from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from loguru import logger


class ThemeManager(QObject):
    """Manages application themes"""

    # Signal emitted when theme changes
    theme_changed = Signal(str)  # Emits new theme name

    LIGHT_THEME = "light"
    DARK_THEME = "dark"

    def __init__(self):
        super().__init__()
        self.current_theme = self.LIGHT_THEME
        self.themes_dir = Path(__file__).parent.parent / "themes"

    def load_theme(self, theme_name: str):
        """Load and apply a theme"""
        qss_file = self.themes_dir / f"{theme_name}.qss"

        if not qss_file.exists():
            logger.warning(f"Theme file not found: {qss_file}")
            return False

        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                stylesheet = f.read()

            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                self.theme_changed.emit(theme_name)  # Emit signal
                logger.info(f"Theme applied: {theme_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to load theme {theme_name}: {e}")
            return False

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme == self.LIGHT_THEME:
            self.load_theme(self.DARK_THEME)
        else:
            self.load_theme(self.LIGHT_THEME)

        return self.current_theme

    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get or create global theme manager"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
