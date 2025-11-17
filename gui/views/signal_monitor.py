"""
Signal Monitor View - Real-time I/O display with AI explanation
"""

from typing import Optional
from PySide6.QtCore import Qt, QTimer, Signal as PySignal, QSize
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
)
from PySide6.QtGui import QFont, QColor, QIcon


class SignalMonitorView(QWidget):
    """Signal monitoring view with real-time updates"""

    # Signal for requesting AI explanation
    signal_explain_requested = PySignal(str)

    def __init__(self, plc):
        super().__init__()
        self.plc = plc
        self._setup_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_signals)
        self.update_timer.start(500)  # Update every 500ms

    def _setup_ui(self) -> None:
        """Setup UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Live Signal Monitor")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        layout.addWidget(title)

        # Signals table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setHorizontalHeaderLabels(
            ["Signal Name", "Type", "Value", "Unit", "Status", "Actions"]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Populate table initially
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate table with signals"""
        signals = self.plc.get_all_signals()
        self.table.setRowCount(len(signals))

        for row, (name, signal) in enumerate(signals.items()):
            # Signal name
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            # Type
            type_item = QTableWidgetItem(signal.type.value)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, type_item)

            # Value (will be updated)
            value_item = QTableWidgetItem(str(signal.value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, value_item)

            # Unit
            unit_item = QTableWidgetItem(signal.unit or "-")
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, unit_item)

            # Status (will be updated)
            status_item = QTableWidgetItem("●")
            status_item.setFont(QFont("Arial", 26))
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, status_item)

            # AI Explain button
            explain_btn = QPushButton("Explain")
            explain_btn.setIconSize(QSize(28, 28))
            explain_btn.setIcon(QIcon(":/icons/icons/chat-bot.png"))
            explain_btn.setMaximumWidth(100)
            explain_btn.clicked.connect(lambda checked=False, s=name: self._on_explain_clicked(s))
            self.table.setCellWidget(row, 5, explain_btn)

    def _update_signals(self) -> None:
        """Update signal values in table"""
        signals = self.plc.get_all_signals()

        for row, (name, signal) in enumerate(signals.items()):
            # Update value
            value_item = self.table.item(row, 2)
            if isinstance(signal.value, float):
                value_item.setText(f"{signal.value:.2f}")
            else:
                value_item.setText(str(signal.value))

            # Update status indicator
            status_item = self.table.item(row, 4)

            if signal.type.value.startswith("DIGITAL"):
                # Digital signals
                if signal.value:
                    status_item.setForeground(QColor("green"))
                else:
                    status_item.setForeground(QColor("gray"))
            else:
                # Analog signals - check alarm threshold
                if signal.alarm_threshold and signal.value >= signal.alarm_threshold:
                    status_item.setForeground(QColor("red"))
                    value_item.setBackground(QColor(255, 200, 200))
                else:
                    status_item.setForeground(QColor("green"))
                    value_item.setBackground(QColor(255, 255, 255))

    def _on_explain_clicked(self, signal_name: str) -> None:
        """Handle explain button click"""
        self.signal_explain_requested.emit(signal_name)
