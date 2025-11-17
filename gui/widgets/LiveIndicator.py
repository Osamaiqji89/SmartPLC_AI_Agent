from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class LiveIndicator(QWidget):
    """Custom live indicator widget with blinking circle"""

    def __init__(self, size=30, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.is_active = False
        self.blink_state = False
        self.color = QColor("#4CAF50")  # Green

    def set_color(self, color: QColor):
        """Set indicator color"""
        self.color = color
        self.update()

    def set_active(self, active: bool):
        """Set active state"""
        self.is_active = active
        self.update()

    def toggle_blink(self):
        """Toggle blink state for animation"""
        if self.is_active:
            self.blink_state = not self.blink_state
            self.update()

    def paintEvent(self, event):
        """Paint the indicator circle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Determine color based on state
        if self.is_active:
            color = QColor("#4CAF50") if self.blink_state else QColor("#A5D6A7")
        else:
            color = QColor("#95a5a6")

        # Draw circle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(2, 2, self.size - 4, self.size - 4)
