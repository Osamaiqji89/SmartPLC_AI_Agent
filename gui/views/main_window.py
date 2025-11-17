"""
Main Window - SmartPLC AI Agent
Central GUI with UI file loading
"""
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QTimer, QFile
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from loguru import logger

from core.plc.mock_plc import get_plc
from gui.views.dashboard import DashboardView
from gui.views.signal_monitor import SignalMonitorView
from gui.widgets.ai_chat import AIChatView
from gui.views.parameter_editor import ParameterEditorView
from gui.views.plc_control import PLCControlView
from gui.core.theme_manager import get_theme_manager
import gui.resources_rc


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # PLC instance
        self.plc = get_plc()
        
        # Load UI file
        self._load_ui()
        
        # Setup views and connections
        self._setup_views()
        self._setup_connections()
        
        # Start PLC simulation
        self.plc.start()
        
        # Setup PLC status update timer
        self.plc_status_timer = QTimer()
        self.plc_status_timer.timeout.connect(self._update_plc_button_states)
        self.plc_status_timer.start(1000)  # Update every second
        
        logger.info("Main window initialized")
    
    def _load_ui(self) -> None:
        """Load UI from .ui file"""
        ui_file_path = Path(__file__).parent.parent / "ui" / "MainWindow.ui"
        
        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)
        
        ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Copy all attributes from loaded UI to self
        for attr in dir(ui):
            if not attr.startswith('_') and attr not in ['parent', 'staticMetaObject']:
                try:
                    setattr(self, attr, getattr(ui, attr))
                except Exception as e:
                    logger.debug(f"Could not copy attribute {attr}: {e}")
        
        # Set central widget
        if hasattr(ui, 'centralwidget'):
            self.setCentralWidget(ui.centralwidget)
        
        # Set window properties
        self.setWindowTitle("SmartPLC AI Agent")
        
        # AI Chat is hidden by default
        self.ai_chat_visible = False
        if hasattr(self, 'glAIChat'):
            # Find parent widget of the layout
            container = self.glAIChat.parentWidget()
            if container:
                container.setVisible(False)
        
        logger.info("UI file loaded successfully")
    
    def _setup_views(self) -> None:
        """Setup view instances and add to stacked widget"""
        # Create views
        self.dashboard_view = DashboardView(self.plc)
        self.signal_monitor_view = SignalMonitorView(self.plc)
        self.parameter_view = ParameterEditorView()
        self.plc_control_view = PLCControlView(self.plc)
        self.ai_chat_view = AIChatView()
        self.btnDashboard.setChecked(True)
        self.setFont(QFont("Roboto"))
        # Add views to stacked widget pages
        if hasattr(self, 'stackedWidgetHome'):
            # Add dashboard to page 0
            page0 = self.stackedWidgetHome.widget(0)
            if page0 and page0.layout():
                page0.layout().addWidget(self.dashboard_view)
            
            # Add signal monitor to page 1
            page1 = self.stackedWidgetHome.widget(1)
            if page1 and page1.layout():
                page1.layout().addWidget(self.signal_monitor_view)
            
            # Add parameter editor to page 2
            page2 = self.stackedWidgetHome.widget(2)
            if page2 and page2.layout():
                page2.layout().addWidget(self.parameter_view)

            # Add PLC Control Center to page 3
            page3 = self.stackedWidgetHome.widget(3)
            if page3 and page3.layout():
                page3.layout().addWidget(self.plc_control_view, 0, 0)
            
            # Set default page to Dashboard
            self.stackedWidgetHome.setCurrentIndex(0)
            logger.info(f"Added views to {self.stackedWidgetHome.count()} pages")
        
        # Add AI Chat to glAIChat layout
        if hasattr(self, 'glAIChat'):
            self.glAIChat.addWidget(self.ai_chat_view, 0, 0)
            logger.info("AI Chat view added to layout")
        if hasattr(self, 'splitter'):
            # Splitter-Größen setzen: leftWidget nimmt den Rest, rightWidget bekommt 400px
            sizes = [self.width() - 400, 400]  # leftWidget | rightWidget (400px)
            self.splitter.setSizes(sizes)
            # Enable hover tracking for splitter handle
            self.splitter.handle(1).setAttribute(Qt.WA_Hover, True)
        logger.info("Views setup complete")
    
    def _setup_connections(self) -> None:
        """Setup button connections"""
        # Navigation buttons for stacked widget
        if hasattr(self, 'btnDashboard'):
            self.btnDashboard.clicked.connect(lambda: self._navigate_to(0))
            logger.debug("btnDashboard connected")
        
        if hasattr(self, 'btnSignalMonitor'):
            self.btnSignalMonitor.clicked.connect(lambda: self._navigate_to(1))
            logger.debug("btnSignalMonitor connected")
        
        if hasattr(self, 'btnParameter'):
            self.btnParameter.clicked.connect(lambda: self._navigate_to(2))
            logger.debug("btnParameter connected")
        
        if hasattr(self, 'btnPLCControlCenter'):
            self.btnPLCControlCenter.clicked.connect(lambda: self._navigate_to(3))
            logger.debug("btnPLCControlCenter connected")
        
        # AI Chat toggle
        if hasattr(self, 'btnAIChat'):
            self.btnAIChat.clicked.connect(self._toggle_ai_chat)
            logger.debug("btnAIChat connected")
        
        # Theme toggle
        if hasattr(self, 'btnTheme'):
            self.btnTheme.clicked.connect(self._toggle_theme)
            logger.debug("btnTheme connected")
        
        # Help button
        if hasattr(self, 'btnHelp'):
            self.btnHelp.clicked.connect(self._show_help)
            logger.debug("btnHelp connected")
        
        # PLC Control buttons
        if hasattr(self, 'btnStartPLC'):
            self.btnStartPLC.clicked.connect(self._start_plc)
            logger.debug("btnStartPLC connected")
        
        if hasattr(self, 'btnStopPLC'):
            self.btnStopPLC.clicked.connect(self._stop_plc)
            logger.debug("btnStopPLC connected")
        
        if hasattr(self, 'btnResetPLC'):
            self.btnResetPLC.clicked.connect(self._reset_plc)
            logger.debug("btnResetPLC connected")
        
        # Connect signal explanation request from signal monitor to AI chat
        self.signal_monitor_view.signal_explain_requested.connect(
            self._on_signal_explain_requested
        )
        
        # Update PLC button states initially
        self._update_plc_button_states()
        
        logger.info("All button connections setup complete")
    
    def _navigate_to(self, index: int):
        """Navigate to stacked widget page"""
        if hasattr(self, 'stackedWidgetHome'):
            self.stackedWidgetHome.setCurrentIndex(index)
            page_names = ["Dashboard", "Signal Monitor", "Parameter Editor", "PLC Control Center"]
            page_name = page_names[index] if index < len(page_names) else f"Page {index}"
            logger.debug(f"Navigated to {page_name} (index {index})")
            self.btnDashboard.setChecked(index == 0)
            self.btnSignalMonitor.setChecked(index == 1)
            self.btnParameter.setChecked(index == 2)
            if hasattr(self, 'btnPLCControlCenter'):
                self.btnPLCControlCenter.setChecked(index == 3)
    
    def _toggle_ai_chat(self) -> None:
        """Toggle AI chat visibility"""
        if hasattr(self, 'glAIChat'):
            container = self.glAIChat.parentWidget()
            if container:
                self.ai_chat_visible = not self.ai_chat_visible
                container.setVisible(self.ai_chat_visible)
                state = "shown" if self.ai_chat_visible else "hidden"
                logger.info(f"AI Chat {state}")
    
    def _toggle_theme(self) -> None:
        """Toggle between light and dark theme"""
        theme_manager = get_theme_manager()
        new_theme = theme_manager.toggle_theme()
        logger.info(f"Theme switched to: {new_theme}")
    
    def _show_help(self) -> None:
        """Show help dialog"""
        QMessageBox.information(
            self,
            "Hilfe - SmartPLC AI Agent",
            "SmartPLC AI Agent\n\n"
            "Navigation:\n"
            "• Dashboard - Übersicht der PLC-Daten und Status\n"
            "• Signal Monitor - Live-Signalüberwachung mit Charts\n"
            "• Parameter - Parameter bearbeiten und konfigurieren\n"
            "• AI Chat - AI-Assistent ein/ausblenden\n"
            "• Theme - Hell/Dunkel Modus wechseln\n\n"
            "Features:\n"
            "• 🤖 Signal-Erklärung mit KI (GPT-3.5-Turbo)\n"
            "• 📊 Echtzeit-Datenvisualisierung\n"
            "• ⚙️ Parameterkonfiguration\n"
            "• 📚 RAG-basierte Wissensdatenbank\n\n"
            "Tipp: Klicken Sie auf 🤖 neben einem Signal\n"
            "für eine KI-gestützte Erklärung."
        )
    
    def _on_signal_explain_requested(self, signal_name: str) -> None:
        """Handle signal explanation request from SignalMonitor"""
        logger.info(f"Signal explanation requested: {signal_name}")
        
        # Show AI Chat if hidden
        if not self.ai_chat_visible:
            self._toggle_ai_chat()
        
        # Request explanation in AI Chat view
        self.ai_chat_view.explain_signal(signal_name)
    
    def _start_plc(self) -> None:
        """Start PLC simulation"""
        if not self.plc._running:
            self.plc.start()
            logger.info("PLC simulation started")
            QMessageBox.information(
                self,
                "PLC Start",
                "PLC Simulation gestartet!\n\nDie Prozesssimulation läuft jetzt."
            )
            self._update_plc_button_states()
        else:
            QMessageBox.warning(
                self,
                "PLC Start",
                "PLC läuft bereits!"
            )
    
    def _stop_plc(self) -> None:
        """Stop PLC simulation"""
        if self.plc._running:
            reply = QMessageBox.question(
                self,
                "PLC Stop",
                "Möchten Sie die PLC-Simulation wirklich stoppen?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.plc.stop()
                logger.info("PLC simulation stopped")
                QMessageBox.information(
                    self,
                    "PLC Stop",
                    "PLC Simulation gestoppt!"
                )
                self._update_plc_button_states()
        else:
            QMessageBox.warning(
                self,
                "PLC Stop",
                "PLC läuft nicht!"
            )
    
    def _reset_plc(self) -> None:
        """Reset PLC to initial state"""
        reply = QMessageBox.question(
            self,
            "PLC Reset",
            "PLC auf Anfangszustand zurücksetzen?\n\nAlle Ausgänge werden ausgeschaltet.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Turn off all digital outputs
            do_signals = ["DO_01_Pump", "DO_02_DrainValve", "DO_03_Motor", "DO_04_Stopper"]
            for signal_name in do_signals:
                try:
                    self.plc.write_signal(signal_name, False)
                except Exception as e:
                    logger.warning(f"Could not reset {signal_name}: {e}")
            
            # Reset analog outputs to default values
            ao_defaults = {
                "AO_01_FlowControl": 50.0,      # Default 50% flow
                "AO_02_MotorSpeed": 50.0,       # Default 50% motor speed
                "AO_03_HeatingPower": 0.0       # Default 0% heating
            }
            for signal_name, default_value in ao_defaults.items():
                try:
                    self.plc.write_signal(signal_name, default_value)
                except Exception as e:
                    logger.warning(f"Could not reset {signal_name}: {e}")
            
            logger.info("PLC reset - all outputs cleared")
            QMessageBox.information(
                self,
                "PLC Reset",
                "PLC wurde zurückgesetzt!\n\nAlle Ausgänge sind jetzt AUS."
            )
    
    def _update_plc_button_states(self) -> None:
        """Update PLC button enabled/disabled states based on PLC status"""
        is_running = self.plc._running
        
        if hasattr(self, 'btnStartPLC'):
            self.btnStartPLC.setEnabled(not is_running)
        
        if hasattr(self, 'btnStopPLC'):
            self.btnStopPLC.setEnabled(is_running)
        
        # Connect button is always enabled
        if hasattr(self, 'btnResetPLC'):
            self.btnResetPLC.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Beenden bestätigen",
            "Möchten Sie die Anwendung wirklich beenden?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop PLC simulation
            if self.plc._running:
                self.plc.stop()
            logger.info("Application closing - PLC stopped")
            event.accept()
        else:
            event.ignore()
