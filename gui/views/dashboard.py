"""
Dashboard View - Overview of PLC status
"""

from datetime import datetime

from loguru import logger
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from gui.widgets import BarChartWidget, GaugeWidget, LiveIndicator


class DashboardView(QWidget):
    """Dashboard with PLC status overview"""

    def __init__(self, plc):
        super().__init__()
        self.plc = plc
        self.blink_state = False  # For blinking live indicator
        self.start_time = datetime.now()  # Track PLC start time
        self.was_running = False  # Track previous PLC state
        self._setup_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_dashboard)
        self.update_timer.start(1000)  # Update every second

        # Blink timer for live indicator
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.blink_timer.start(500)  # Blink every 500ms

    def _setup_ui(self) -> None:
        """Setup dashboard UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("PLC Dashboard")
        title.setFont(QFont("Roboto", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        # Status cards
        cards_layout = QHBoxLayout()

        # PLC Status Card
        self.status_card = self._create_status_card()
        cards_layout.addWidget(self.status_card)

        # Signals Card
        self.signals_card = self._create_signals_card()
        cards_layout.addWidget(self.signals_card)

        # Alarms Card
        self.alarms_card = self._create_alarms_card()
        cards_layout.addWidget(self.alarms_card)

        layout.addLayout(cards_layout)

        # Process status
        self.process_group = self._create_process_status()
        layout.addWidget(self.process_group)

        layout.addStretch()
        self.setLayout(layout)

    def _create_status_card(self) -> QGroupBox:
        """Create PLC status card"""
        group = QGroupBox("PLC Status")
        layout = QGridLayout()

        # Live indicator with status
        status_layout = QHBoxLayout()
        self.live_indicator = LiveIndicator(28)
        status_layout.addWidget(self.live_indicator)

        self.connection_label = QLabel("RUNNING")
        self.connection_label.setFont(QFont("Roboto", 14, QFont.Bold))
        self.connection_label.setStyleSheet("color: #4CAF50;")
        status_layout.addWidget(self.connection_label)
        status_layout.addStretch()

        layout.addLayout(status_layout, 0, 0, 1, 2)

        layout.addWidget(QLabel("Mode:"), 1, 0)
        self.mode_label = QLabel("Simulation")
        layout.addWidget(self.mode_label, 1, 1)

        layout.addWidget(QLabel("Uptime:"), 2, 0)
        self.uptime_label = QLabel("0s")
        layout.addWidget(self.uptime_label, 2, 1)

        group.setLayout(layout)
        return group

    def _create_signals_card(self) -> QGroupBox:
        """Create signals summary card"""
        group = QGroupBox("Signals")
        layout = QGridLayout()

        layout.addWidget(QLabel("Total Signals:"), 0, 0)
        self.total_signals_label = QLabel("0")
        self.total_signals_label.setFont(QFont("Roboto", 14, QFont.Bold))
        layout.addWidget(self.total_signals_label, 0, 1)

        layout.addWidget(QLabel("Active:"), 1, 0)
        self.active_signals_label = QLabel("0")
        layout.addWidget(self.active_signals_label, 1, 1)

        group.setLayout(layout)
        return group

    def _create_alarms_card(self) -> QGroupBox:
        """Create alarms card with active alarms table"""
        group = QGroupBox("Alarms")
        # group.setMaximumWidth(350)
        # group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout = QVBoxLayout()

        # Header with alarm count
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Active Alarms:")
        self.title_label.setMaximumWidth(50)
        header_layout.addWidget(self.title_label)
        self.active_alarms_label = QLabel("0")
        self.active_alarms_label.setMaximumWidth(50)
        self.active_alarms_label.setFont(QFont("Roboto", 14, QFont.Bold))
        self.active_alarms_label.setStyleSheet("color: #4CAF50;")  # Green when no alarms
        header_layout.addWidget(self.active_alarms_label)
        layout.addLayout(header_layout)

        # Active alarms table
        self.alarms_table = QTableWidget()
        self.alarms_table.setColumnCount(3)
        self.alarms_table.setHorizontalHeaderLabels(["Signal", "Value", "Threshold"])
        self.alarms_table.verticalHeader().setVisible(False)
        self.alarms_table.setMaximumHeight(150)
        self.alarms_table.setMaximumWidth(280)
        self.alarms_table.setAlternatingRowColors(True)
        self.alarms_table.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.alarms_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alarms_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Column sizing
        header = self.alarms_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout.addWidget(self.alarms_table)

        group.setLayout(layout)
        return group

    def _create_process_status(self) -> QGroupBox:
        """Create process status display with modern visualizations"""
        group = QGroupBox("Process Status")
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Left side - Tank/Pump with bar chart
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)

        # Bar chart for tank level
        self.tank_bar = BarChartWidget()
        self.tank_bar.setMinimumSize(250, 250)
        left_layout.addWidget(self.tank_bar, 0, Qt.AlignCenter)

        # Pump status label
        self.pump_status_label = QLabel("Pump Status: ⚫ OFF")
        self.pump_status_label.setFont(QFont("Roboto", 10))
        self.pump_status_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.pump_status_label)

        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)

        # Right side - Pressure gauge and motor info
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)

        # Pressure gauge
        self.pressure_gauge = GaugeWidget()
        self.pressure_gauge.setMinimumSize(250, 150)
        right_layout.addWidget(self.pressure_gauge, 0, Qt.AlignCenter)

        # Info labels
        self.pressure_label = QLabel("Pressure: 0.00 bar")
        self.pressure_label.setFont(QFont("Roboto", 10))
        self.pressure_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.pressure_label)

        self.conveyor_speed_label = QLabel("Conveyor Speed: 0.0 m.min")
        self.conveyor_speed_label.setFont(QFont("Roboto", 9))
        self.conveyor_speed_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.conveyor_speed_label)

        self.motor_status_label = QLabel("Motor Status: OFF ⚫")
        self.motor_status_label.setFont(QFont("Roboto", 9))
        self.motor_status_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.motor_status_label)

        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)

        group.setLayout(layout)
        return group

    def _update_dashboard(self) -> None:
        """Update dashboard values"""
        try:
            # Update PLC status
            is_running = self.plc._running

            # Detect PLC start transition
            if is_running and not self.was_running:
                self.start_time = datetime.now()  # Reset uptime counter
            self.was_running = is_running

            if hasattr(self, "live_indicator"):
                self.live_indicator.set_active(is_running)

            if is_running:
                self.connection_label.setText("RUNNING")
                self.connection_label.setStyleSheet("color: #4CAF50;  font-weight: bold;")

                # Update uptime
                uptime = datetime.now() - self.start_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.connection_label.setText("STOPPED")
                self.connection_label.setStyleSheet("color: #e74c3c;  font-weight: bold;")
                self.uptime_label.setText("00:00:00")

            # Update signal counts
            signals = self.plc.get_all_signals()
            self.total_signals_label.setText(str(len(signals)))

            # Count active signals (Digital: True, Analog: > 0)
            active_count = 0
            for signal in signals.values():
                if signal.type.value.startswith("DIGITAL"):
                    # Digital signals: count if True
                    if signal.value is True:
                        active_count += 1
                else:
                    # Analog signals: count if > 0
                    if isinstance(signal.value, (int, float)) and signal.value > 0:
                        active_count += 1

            self.active_signals_label.setText(str(active_count))

            # Update tank level bar chart
            tank_level = self.plc.read_signal("AI_01_TankLevel")
            self.tank_bar.set_value(tank_level)

            # Update pump status
            pump_on = self.plc.read_signal("DO_01_Pump")
            self.pump_status_label.setText(f"Pump Status: {'🟢 ON' if pump_on else '⚫ OFF'}")
            self.pump_status_label.setStyleSheet("color: green;" if pump_on else "color: gray;")

            # Update pressure gauge
            pressure = self.plc.read_signal("AI_02_PressureSensor")
            self.pressure_gauge.set_value(pressure)
            self.pressure_label.setText(f"Pressure: {pressure:.2f} bar")

            # Update conveyor/motor
            speed = self.plc.read_signal("AI_03_BeltSpeed")
            self.conveyor_speed_label.setText(f"Conveyor Speed: {speed:.1f} m.min")

            motor_on = self.plc.read_signal("DO_03_Motor")
            self.motor_status_label.setText(f"Motor Status: {'ON 🟢' if motor_on else 'OFF ⚫'}")
            self.motor_status_label.setStyleSheet("color: green;" if motor_on else "color: gray;")

            # Check for alarms
            self._check_alarms()

        except Exception as e:
            logger.error(f"Dashboard update error: {e}")

    def _toggle_blink(self) -> None:
        """Toggle blink state for live indicator"""
        if hasattr(self, "live_indicator"):
            self.live_indicator.toggle_blink()

    def _check_alarms(self) -> None:
        """Check for active alarms and update table"""
        from PySide6.QtWidgets import QTableWidgetItem

        active_alarms = []

        try:
            # Get all signals from PLC
            signals = self.plc.get_all_signals()

            # Check each signal for alarm threshold
            for signal_name, signal in signals.items():
                if signal.alarm_threshold is not None and signal.value is not None:
                    # Check if value exceeds threshold
                    if (
                        isinstance(signal.value, (int, float))
                        and signal.value > signal.alarm_threshold
                    ):
                        active_alarms.append(
                            {
                                "signal": signal_name,
                                "value": signal.value,
                                "threshold": signal.alarm_threshold,
                                "unit": signal.unit or "",
                            }
                        )

            # Update alarm count and color
            alarm_count = len(active_alarms)
            self.active_alarms_label.setText(str(alarm_count))

            if alarm_count == 0:
                self.active_alarms_label.setStyleSheet("color: #4CAF50;")  # Green
            elif alarm_count <= 2:
                self.active_alarms_label.setStyleSheet("color: #FF9800;")  # Orange
            else:
                self.active_alarms_label.setStyleSheet("color: #F44336;")  # Red

            # Update alarms table
            self.alarms_table.setRowCount(len(active_alarms))

            for row, alarm in enumerate(active_alarms):
                # Signal name with warning icon
                signal_item = QTableWidgetItem(f"⚠️ {alarm['signal']}")
                signal_item.setForeground(QColor("#F44336"))  # Red text
                self.alarms_table.setItem(row, 0, signal_item)

                # Current value
                value_text = f"{alarm['value']:.1f} {alarm['unit']}"
                value_item = QTableWidgetItem(value_text)
                value_item.setForeground(QColor("#F44336"))
                self.alarms_table.setItem(row, 1, value_item)

                # Threshold
                threshold_text = f">{alarm['threshold']:.1f} {alarm['unit']}"
                threshold_item = QTableWidgetItem(threshold_text)
                self.alarms_table.setItem(row, 2, threshold_item)

        except Exception as e:
            logger.error(f"Alarm check error: {e}")
