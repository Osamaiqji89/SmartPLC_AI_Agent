"""
PLC Control Center - Complete I/O Control and Monitoring
Professional SCADA-style interface for PLC control
"""

from datetime import datetime

from loguru import logger
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from gui.widgets import LiveIndicator


class PLCControlView(QWidget):
    """
    Complete PLC Control Center
    Provides full I/O control and monitoring capabilities
    """

    def __init__(self, plc, parent=None):
        super().__init__(parent)
        self.plc = plc
        self.start_time = datetime.now()

        # UI Setup
        self._setup_ui()

        # Timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)  # Update every second

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink_indicator)
        self.blink_timer.start(500)  # Blink every 500ms

        logger.info("PLC Control Center initialized")

    def _setup_ui(self) -> None:
        """Setup the complete UI layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

        # Title
        title = QLabel("PLC Control Center")
        title.setFont(QFont("Roboto", 14, QFont.Bold))
        main_layout.addWidget(title)

        # Grid layout for compact arrangement
        grid = QGridLayout()
        grid.setSpacing(5)

        # Row 0: Status & Control (spans 2 columns)
        grid.addWidget(self._create_status_control(), 0, 0, 1, 2)

        # Row 1: Digital I/O side by side
        grid.addWidget(self._create_digital_inputs(), 1, 0)
        grid.addWidget(self._create_digital_outputs(), 1, 1)

        # Row 2: Analog I/O side by side
        grid.addWidget(self._create_analog_inputs(), 2, 0)
        grid.addWidget(self._create_analog_outputs(), 2, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _create_status_control(self) -> QGroupBox:
        """Create status and control section"""
        group = QGroupBox("Status & Steuerung")
        layout = QHBoxLayout()
        layout.setSpacing(5)

        # Live indicator
        self.live_indicator = LiveIndicator(28)
        layout.addWidget(self.live_indicator)

        # Status label
        self.status_label = QLabel("STOPPED")
        self.status_label.setFont(QFont("Roboto", 14, QFont.Bold))
        self.status_label.setStyleSheet("color: #E74C3C;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Uptime
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setFont(QFont("Roboto", 10))
        layout.addWidget(self.uptime_label)

        group.setLayout(layout)
        return group

    def _create_digital_inputs(self) -> QGroupBox:
        """Create digital inputs section"""
        group = QGroupBox("Digital Inputs (Sensoren)")
        layout = QVBoxLayout()
        layout.setSpacing(3)

        self.di_labels = {}
        di_signals = [
            ("DI_01_StartButton", "Start Button"),
            ("DI_02_StopButton", "Stop Button"),
            ("DI_03_ObjectSensor", "Objekt Sensor"),
            ("DI_04_LimitSwitch", "Endschalter"),
        ]

        for signal_name, label_text in di_signals:
            row = QHBoxLayout()
            label = QLabel(f"● {label_text}")
            label.setFont(QFont("Roboto", 10))
            self.di_labels[signal_name] = label
            row.addWidget(label)
            row.addStretch()
            layout.addLayout(row)

        group.setLayout(layout)
        return group

    def _create_digital_outputs(self) -> QGroupBox:
        """Create digital outputs section"""
        group = QGroupBox("Digital Outputs (Aktoren)")
        layout = QVBoxLayout()
        layout.setSpacing(3)

        self.do_checkboxes = {}
        do_signals = [
            ("DO_01_Pump", "Pumpe"),
            ("DO_02_DrainValve", "Ablassventil"),
            ("DO_03_Motor", "Förderband Motor"),
            ("DO_04_Stopper", "Stopper Zylinder"),
        ]

        for signal_name, label_text in do_signals:
            cb = QCheckBox(f"{label_text}")
            cb.setFont(QFont("Roboto", 10))
            cb.stateChanged.connect(
                lambda checked, sig=signal_name: self._toggle_output(sig, checked)
            )
            self.do_checkboxes[signal_name] = cb
            layout.addWidget(cb)

        group.setLayout(layout)
        return group

    def _create_analog_inputs(self) -> QGroupBox:
        """Create analog inputs section"""
        group = QGroupBox("Analog Inputs (Messungen)")
        layout = QVBoxLayout()
        layout.setSpacing(3)

        self.ai_labels = {}
        ai_signals = [
            ("AI_01_TankLevel", "Tank Level", "%"),
            ("AI_02_PressureSensor", "Druck", "bar"),
            ("AI_03_BeltSpeed", "Bandgeschwindigkeit", "m/min"),
            ("AI_04_CycleCounter", "Zykluszähler", "pcs"),
        ]

        for signal_name, label_text, unit in ai_signals:
            row = QHBoxLayout()
            text_label = QLabel(f"{label_text}:")
            text_label.setFont(QFont("Roboto", 10))
            text_label.setMinimumWidth(120)
            row.addWidget(text_label)

            value_label = QLabel("0.0 " + unit)
            value_label.setFont(QFont("Roboto", 10, QFont.Bold))
            value_label.setStyleSheet("color: #007BFF;")
            self.ai_labels[signal_name] = value_label
            row.addWidget(value_label)
            row.addStretch()

            layout.addLayout(row)

        group.setLayout(layout)
        return group

    def _create_analog_outputs(self) -> QGroupBox:
        """Create analog outputs section"""
        group = QGroupBox("Analog Outputs (Steuerung)")
        layout = QVBoxLayout()
        layout.setSpacing(3)

        self.ao_sliders = {}
        ao_signals = [
            ("AO_01_FlowControl", "Durchfluss-Regelventil"),
            ("AO_02_MotorSpeed", "Motor-Geschwindigkeit"),
        ]

        for signal_name, label_text in ao_signals:
            # Label
            label = QLabel(f"{label_text}: 0%")
            label.setFont(QFont("Roboto", 10))
            layout.addWidget(label)

            # Slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(
                50 if "Motor" in label_text or "Flow" in label_text else 0
            )  # Default 50% for motor and flow
            slider.valueChanged.connect(
                lambda value, sig=signal_name, lbl=label: self._update_analog_output(
                    sig, value, lbl
                )
            )
            self.ao_sliders[signal_name] = (slider, label)
            layout.addWidget(slider)

        group.setLayout(layout)
        return group

    def _start_plc(self) -> None:
        """Start PLC"""
        if not self.plc._running:
            self.plc.start()
            self.start_time = datetime.now()
            logger.info("PLC started from Control Center")

    def _stop_plc(self) -> None:
        """Stop PLC"""
        if self.plc._running:
            self.plc.stop()
            logger.info("PLC stopped from Control Center")

    def _reset_plc(self) -> None:
        """Reset PLC outputs"""
        # Turn off all digital outputs
        for signal_name in self.do_checkboxes.keys():
            try:
                self.plc.write_signal(signal_name, False)
            except Exception as e:
                logger.warning(f"Could not reset {signal_name}: {e}")

        # Reset analog outputs to default values
        for signal_name, (slider, label) in self.ao_sliders.items():
            try:
                default_value = 50.0 if "Motor" in signal_name or "Flow" in signal_name else 0.0
                self.plc.write_signal(signal_name, default_value)
                slider.setValue(int(default_value))
                label.setText(f"{label.text().split(':')[0]}: {int(default_value)}%")
            except Exception as e:
                logger.warning(f"Could not reset {signal_name}: {e}")

        logger.info("PLC reset from Control Center")

    def _toggle_output(self, signal_name: str, value: bool) -> None:
        """Toggle digital output"""
        try:
            self.plc.write_signal(signal_name, value)
        except Exception as e:
            logger.error(f"Error toggling {signal_name}: {e}")

    def _update_analog_output(self, signal_name: str, value: int, label: QLabel) -> None:
        """Update analog output value"""
        try:
            self.plc.write_signal(signal_name, float(value))
            label.setText(f"{label.text().split(':')[0]}: {value}%")
        except Exception as e:
            logger.error(f"Error updating {signal_name}: {e}")

    def _blink_indicator(self) -> None:
        """Toggle blink state"""
        if hasattr(self, "live_indicator"):
            self.live_indicator.toggle_blink()

    def _update_data(self) -> None:
        """Update all displayed data"""
        is_running = self.plc._running

        # Update status
        if hasattr(self, "live_indicator"):
            self.live_indicator.set_active(is_running)

        if hasattr(self, "status_label"):
            if is_running:
                self.status_label.setText("RUNNING")
                self.status_label.setStyleSheet("color: #27AE60;")
            else:
                self.status_label.setText("STOPPED")
                self.status_label.setStyleSheet("color: #E74C3C;")

        # Update buttons
        if hasattr(self, "btn_start"):
            self.btn_start.setEnabled(not is_running)
        if hasattr(self, "btn_stop"):
            self.btn_stop.setEnabled(is_running)

        # Update uptime
        if is_running and hasattr(self, "uptime_label"):
            uptime = datetime.now() - self.start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.uptime_label.setText(f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # Update digital inputs
        for signal_name, label in self.di_labels.items():
            try:
                value = self.plc.read_signal(signal_name)
                if value:
                    label.setText(f"🟢 {label.text().split(' ', 1)[1]}")
                    label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                else:
                    label.setText(f"⚫ {label.text().split(' ', 1)[1]}")
                    label.setStyleSheet("color: #95a5a6;")
            except Exception as e:
                logger.debug(f"Error reading {signal_name}: {e}")

        # Update digital outputs checkboxes
        for signal_name, cb in self.do_checkboxes.items():
            try:
                value = self.plc.read_signal(signal_name)
                cb.blockSignals(True)
                cb.setChecked(bool(value))
                cb.blockSignals(False)
            except Exception as e:
                logger.debug(f"Error updating {signal_name}: {e}")

        # Update analog inputs
        for signal_name, label in self.ai_labels.items():
            try:
                value = self.plc.read_signal(signal_name)
                unit = label.text().split()[-1]

                # Format based on signal type - all values displayed directly
                if "Counter" in signal_name:
                    label.setText(f"{int(value)} {unit}")
                else:
                    label.setText(f"{value:.1f} {unit}")
            except Exception as e:
                logger.debug(f"Error reading {signal_name}: {e}")

        # Update analog output sliders
        for signal_name, (slider, label) in self.ao_sliders.items():
            try:
                value = self.plc.read_signal(signal_name)
                slider.blockSignals(True)
                slider.setValue(int(value))
                slider.blockSignals(False)
                label.setText(f"{label.text().split(':')[0]}: {int(value)}%")
            except Exception as e:
                logger.debug(f"Error updating {signal_name}: {e}")
