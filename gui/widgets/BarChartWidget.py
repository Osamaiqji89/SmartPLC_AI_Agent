from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush


class BarChartWidget(QWidget):
    """Vertical bar chart widget for tank level visualization"""

    def __init__(self):
        super().__init__()
        self.value = 0  # 0-100%

    def set_value(self, value):
        """Set bar value (0-100)"""
        self.value = max(0, min(100, value))
        self.update()

    def paintEvent(self, event):
        """Paint the bar chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Transparent background
        painter.fillRect(self.rect(), Qt.transparent)

        # Chart dimensions
        margin = 40
        chart_width = self.width() - margin * 2
        chart_height = self.height() - margin * 2

        # Draw Y-axis
        painter.setPen(QPen(QColor("#666666"), 2))
        painter.drawLine(margin, margin, margin, self.height() - margin)

        # Draw X-axis
        painter.drawLine(
            margin, self.height() - margin, self.width() - margin, self.height() - margin
        )

        # Y-axis labels (0%, 50%, 100%)
        painter.setFont(QFont("Roboto", 8))
        painter.setPen(QPen(QColor("#666666")))
        painter.drawText(5, self.height() - margin + 5, "0%")
        painter.drawText(5, margin + chart_height // 2 + 5, "50%")
        painter.drawText(5, margin + 5, "100%")

        # Bar dimensions
        bar_width = 60
        bar_x = margin + 20
        bar_max_height = chart_height - 10

        # Calculate fill height
        fill_height = int(bar_max_height * (self.value / 100))
        fill_y = self.height() - margin - fill_height

        # Draw bar background (white/light gray)
        painter.setPen(QPen(QColor("#ebedf3"), 1))
        painter.setBrush(QBrush(QColor("#ebedf3")))
        painter.drawRect(bar_x, margin + 5, bar_width, bar_max_height)

        # Draw filled portion (orange) - from bottom up
        painter.setBrush(QBrush(QColor("#FF9800")))
        painter.setPen(Qt.NoPen)
        painter.drawRect(bar_x, fill_y, bar_width, fill_height)

        # Draw percentage text next to bar
        painter.setPen(QPen(QColor("#FF9800")))
        painter.setFont(QFont("Roboto", 12, QFont.Bold))
        text = f"{self.value:.1f}%"
        text_x = bar_x + bar_width + 10
        text_y = fill_y + (fill_height // 2) + 5
        if fill_height < 20:  # If bar is too small, show text above
            text_y = fill_y - 5
        painter.drawText(text_x, text_y, text)
