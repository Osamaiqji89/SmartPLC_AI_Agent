from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
import math


class GaugeWidget(QWidget):
    """Semi-circular gauge widget for pressure visualization"""

    def __init__(self):
        super().__init__()
        self.value = 0
        self.max_value = 10  # Max 10 bar

    def set_value(self, value):
        """Set gauge value"""
        self.value = max(0, min(self.max_value, value))
        self.update()

    def paintEvent(self, event):
        """Paint the gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Transparent background
        painter.fillRect(self.rect(), Qt.transparent)

        # Gauge dimensions
        size = min(self.width() - 60, (self.height() - 40) * 2)
        center_x = self.width() // 2
        center_y = self.height() - 10
        radius = size // 2

        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        start_angle = 180 * 16  # Start at bottom (270°)

        # Draw colored segments (green -> yellow -> orange -> red)
        # Green segment (0-40%)
        painter.setPen(QPen(QColor("#4CAF50"), 10))
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(rect, start_angle, int(-144 * 16))  # 40% of 180° = 72°

        # Yellow segment (40-60%)
        painter.setPen(QPen(QColor("#FFEB3B"), 10))
        painter.drawArc(rect, start_angle + int(-72 * 16), int(-32 * 16))  # 20% of 180° = 36°

        # Orange segment (60-80%)
        painter.setPen(QPen(QColor("#FF9800"), 10))
        painter.drawArc(rect, start_angle + int(-110 * 16), int(-32 * 16))  # 20% of 180° = 36°

        # Red segment (80-100%)
        painter.setPen(QPen(QColor("#F44336"), 10))
        painter.drawArc(rect, start_angle + int(-146 * 16), int(-34 * 16))  # 20% of 180° = 36°

        # Draw small tick marks for scale
        painter.setPen(QPen(QColor("#666666"), 1))
        for i in range(11):  # 0 to 10 ticks
            tick_percentage = i / 10
            angle = -90 + (tick_percentage * 180)
            angle_rad = math.radians(angle)

            inner_x = center_x + (radius - 20) * math.cos(angle_rad)
            inner_y = center_y + (radius - 20) * math.sin(angle_rad)
            outer_x = center_x + (radius - 8) * math.cos(angle_rad)
            outer_y = center_y + (radius - 8) * math.sin(angle_rad)

            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

        # Draw needle with color based on value
        percentage = self.value / self.max_value
        needle_angle = 180 + (percentage * 180)
        needle_rad = math.radians(needle_angle)
        needle_length = radius - 25
        needle_x = center_x + needle_length * math.cos(needle_rad)
        needle_y = center_y + needle_length * math.sin(needle_rad)

        # Needle color based on percentage
        if percentage < 0.4:
            needle_color = QColor("#4CAF50")  # Green
        elif percentage < 0.6:
            needle_color = QColor("#FFEB3B")  # Yellow
        elif percentage < 0.8:
            needle_color = QColor("#FF9800")  # Orange
        else:
            needle_color = QColor("#F44336")  # Red

        painter.setPen(QPen(needle_color, 2))
        painter.drawLine(center_x, center_y, int(needle_x), int(needle_y))

        # Draw center circle
        painter.setBrush(QBrush(QColor("#333333")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - 8, center_y - 8, 16, 16)
