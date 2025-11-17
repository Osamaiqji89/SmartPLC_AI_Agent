"""
AI Chat View - Interactive assistant with RAG support
"""
from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QApplication,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QAbstractItemView,
    QSizePolicy
)
from PySide6.QtGui import QFont, QIcon
from gui.core.AIWorker import AIWorker
from gui.core.theme_manager import get_theme_manager

class AIChatView(QWidget):
    """AI Chat interface with RAG support"""
    
    def __init__(self):
        super().__init__()
        self.current_worker = None
        self.icon_label = None  # Store icon label reference
        self._setup_ui()
        
        # Connect to theme changes
        theme_mgr = get_theme_manager()
        theme_mgr.theme_changed.connect(self._update_icon)
    
    def _setup_ui(self):
        """Setup chat UI"""
        layout = QVBoxLayout()
        
        # Title with icon
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0,0,0,0)
        
        # Icon label with theme-aware icon
        self.icon_label = QLabel()
        self._update_icon()  # Set initial icon
        title_layout.addWidget(self.icon_label)
        
        title = QLabel("AI Assistant")
        title.setFont(QFont("Roboto", 14, QFont.Bold))
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Chat display (ListWidget for bubble layout)
        self.chat_display = QListWidget()
        self.chat_display.setFrameStyle(QFrame.NoFrame)
        self.chat_display.setSpacing(4)
        self.chat_display.setWordWrap(True)
        self.chat_display.setSelectionMode(QAbstractItemView.NoSelection)
        self.chat_display.setFocusPolicy(Qt.NoFocus)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        # Scroll settings
        self.chat_display.verticalScrollBar().setSingleStep(5)
        self.chat_display.verticalScrollBar().setPageStep(100)
        
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        # Multi-line input field (QTextEdit instead of QLineEdit)
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Ihre Nachricht...")
        self.input_field.setMinimumHeight(32)
        self.input_field.setMaximumHeight(120)
        self.input_field.setFixedHeight(40)  # Initial klein
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_field.setAcceptRichText(False)  # Nur Plain Text
        
        # Auto-resize bei Texteingabe
        self.input_field.textChanged.connect(self._adjust_input_height)
        
        # Event filter für Enter-Taste
        self.input_field.installEventFilter(self)
        
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("Senden ➤")
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Welcome message
        self._add_system_message(
            "Willkommen! Ich bin Ihr KI-Assistent für PLC-Diagnose und -Konfiguration.\n\n"
            "Klicken Sie auf '🤖 Explain' neben einem Signal im Signal Monitor, "
            "oder stellen Sie hier direkt Fragen."
        )
    
    def explain_signal(self, signal_name: str):
        """Request signal explanation"""
        self._add_user_message(f"Erkläre Signal: {signal_name}")
        
        # Show status IMMEDIATELY (before worker starts)
        self._add_system_message("⏳ Analyisiere Signal...")
        self._disable_input()
        
        # Force UI update
        QApplication.processEvents()
        
        # Start background worker
        self.current_worker = AIWorker("explain_signal", {"signal_name": signal_name})
        self.current_worker.response_ready.connect(self._on_response_received)
        self.current_worker.error_occurred.connect(self._on_error)
        self.current_worker.start()
    
    def _send_message(self):
        """Send user message"""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
        
        self._add_user_message(message)
        self.input_field.clear()
        
        # Start background worker
        self.current_worker = AIWorker("chat", {"message": message})
        self.current_worker.response_ready.connect(self._on_response_received)
        self.current_worker.error_occurred.connect(self._on_error)
        self.current_worker.start()
        
        self._add_system_message("⏳ Denke nach...")
        self._disable_input()
    
    def _adjust_input_height(self):
        """Adjust input field height based on content"""
        doc = self.input_field.document()
        doc_height = int(doc.size().height()) + 16  # Padding
        min_height = 50
        max_height = 120
        new_height = min(max(doc_height, min_height), max_height)
        self.input_field.setFixedHeight(new_height)
    
    def eventFilter(self, obj, event):
        """Filter events for input field"""
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            key_event = event
            
            # Enter ohne Shift → Senden
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if not (key_event.modifiers() & Qt.ShiftModifier):
                    self._send_message()
                    return True  # Event gefiltert
                # Shift+Enter → Neue Zeile (Standard-Verhalten)
        
        return super().eventFilter(obj, event)
    
    def _on_response_received(self, response: str):
        """Handle AI response"""
        self._remove_last_message()  # Remove "thinking" message
        self._add_assistant_message(response)
        self._enable_input()
    
    def _on_error(self, error: str):
        """Handle error"""
        self._remove_last_message()
        self._add_system_message(f"❌ Fehler: {error}")
        self._enable_input()
    
    def _add_user_message(self, message: str):
        """Add user message to chat"""
        self._add_message("User", message)
    
    def _add_assistant_message(self, message: str):
        """Add assistant message to chat"""
        self._add_message("🤖 Assistant", message)
    
    def _add_system_message(self, message: str):
        """Add system message to chat"""
        self._add_message("System", message)
    
    def _add_message(self, sender: str, message: str):
        """Add message to chat display with bubble layout"""
        # Create widget for message
        message_widget = QWidget()
        message_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout = QHBoxLayout(message_widget)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(0)
        
        # Create bubble label
        bubble = QLabel()
        bubble.setWordWrap(True)
        bubble.setTextFormat(Qt.RichText)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        # Max bubble width (70% of chat width)
        max_bubble_width = int(self.chat_display.width() * 0.80)
        bubble.setMaximumWidth(max_bubble_width)
        
        # Process message text (escape HTML, replace newlines, handle bold)
        processed_message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        processed_message = processed_message.replace("\n", "<br>")
        # Bold text: **text** -> <b>text</b>
        import re
        processed_message = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', processed_message)
        
        if sender == "User":
            # User Bubble - Right side, blue
            layout.addStretch(3)
            
            bubble.setText(
                f"<div style='padding: 2px;'>"
                f"<div style='font-size: 9pt; margin-bottom: 4px;'><b>🧑 You</b></div>"
                f"<div style='font-size: 10pt;'>{processed_message}</div>"
                f"</div>"
            )
            
            bubble.setStyleSheet(
                "QLabel { "
                "  background-color: rgba(52, 152, 219, 0.3); "
                "  padding: 6px 6px; "
                "  border-radius: 15px; "
                "}"
            )
            layout.addWidget(bubble, 7)
            
        elif sender.startswith("🤖"):
            # AI Bubble - Left side, green
            bubble.setText(
                f"<div style='padding: 2px;'>"
                f"<div style='font-size: 9pt; margin-bottom: 4px;'><b>🤖 AI Assistant</b></div>"
                f"<div style='font-size: 10pt;'>{processed_message}</div>"
                f"</div>"
            )
            
            bubble.setStyleSheet(
                "QLabel { "
                "  background-color: rgba(146, 201, 255, 0.25); "
                "  padding: 6px 6px; "
                "  border-radius: 15px; "
                "}"
            )
            layout.addWidget(bubble, 7)
            layout.addStretch(3)
            
        else:
            # System message - Centered, gray
            layout.addStretch(1)
            
            bubble.setText(
                f"<div style='padding: 2px; text-align: center;'>"
                f"<div style='font-size: 9pt; color: #888;'>{processed_message}</div>"
                f"</div>"
            )
            
            bubble.setStyleSheet(
                "QLabel { "
                "  background-color: rgba(128, 128, 128, 0.2); "
                "  padding: 6px 12px; "
                "  border-radius: 15px; "
                "}"
            )
            layout.addWidget(bubble, 8)
            layout.addStretch(1)
        
        # Calculate size
        message_widget.adjustSize()
        widget_size = message_widget.sizeHint()
        widget_size.setHeight(widget_size.height() + 10) 
        if (widget_size.height() < 80): {
            widget_size.setHeight(80)  # Mindesthöhe für kleine Nachrichten
        }

        # Add to list
        item = QListWidgetItem(self.chat_display)
        item.setSizeHint(widget_size)
        self.chat_display.addItem(item)
        self.chat_display.setItemWidget(item, message_widget)
        
        # Auto-scroll to bottom
        self.chat_display.scrollToBottom()
    
    def _remove_last_message(self):
        """Remove last message (e.g., loading indicator)"""
        count = self.chat_display.count()
        if count > 0:
            self.chat_display.takeItem(count - 1)
    
    def _disable_input(self):
        """Disable input while processing"""
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
    
    def _enable_input(self):
        """Enable input after processing"""
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_field.setFocus()
    
    def _update_icon(self):
        """Update icon based on current theme"""
        if not self.icon_label:
            return
        
        theme_mgr = get_theme_manager()
        current_theme = theme_mgr.current_theme
        
        # Choose icon based on theme
        if current_theme == "dark":
            icon_path = ":/icons/icons/chat-bot.png"
        else:
            icon_path = ":/icons/icons/chat-botDark.png"
        
        # Update icon
        self.icon_label.setPixmap(QIcon(icon_path).pixmap(30, 30))
