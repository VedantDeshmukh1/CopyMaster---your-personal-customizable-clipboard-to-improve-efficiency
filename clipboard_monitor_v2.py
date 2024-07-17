import sys
import pyperclip
import time
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QLabel, QSpinBox, QStyle, QScrollArea
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont

class ClipboardMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clipboard_history = []
        self.is_monitoring = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Advanced Clipboard Monitor')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit, QScrollArea {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Controls
        controls_layout = QHBoxLayout()
        self.start_stop_button = QPushButton('Start Monitoring')
        self.start_stop_button.clicked.connect(self.toggle_monitoring)
        controls_layout.addWidget(self.start_stop_button)

        self.duration_label = QLabel('Duration (minutes):')
        controls_layout.addWidget(self.duration_label)

        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 1440)  # 1 minute to 24 hours
        self.duration_spinbox.setValue(60)
        controls_layout.addWidget(self.duration_spinbox)

        self.save_button = QPushButton('Save History')
        self.save_button.clicked.connect(self.save_history)
        controls_layout.addWidget(self.save_button)

        layout.addLayout(controls_layout)

        # Clipboard history display
        self.history_scroll = QScrollArea()
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_scroll.setWidget(self.history_widget)
        self.history_scroll.setWidgetResizable(True)
        layout.addWidget(self.history_scroll)

        central_widget.setLayout(layout)

        # System tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Clipboard monitoring
        self.clipboard = QApplication.clipboard()
        self.last_content = self.clipboard.text()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_clipboard)

    def toggle_monitoring(self):
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.duration_spinbox.value())
        self.timer.start(500)  # Check every 500 ms
        self.start_stop_button.setText('Stop Monitoring')
        self.duration_spinbox.setEnabled(False)

    def stop_monitoring(self):
        self.is_monitoring = False
        self.timer.stop()
        self.start_stop_button.setText('Start Monitoring')
        self.duration_spinbox.setEnabled(True)

    def check_clipboard(self):
        current_time = datetime.now()
        if current_time >= self.end_time:
            self.stop_monitoring()
            return

        current_content = self.clipboard.text()
        if current_content != self.last_content:
            self.last_content = current_content
            self.add_history_item(current_content)

    def add_history_item(self, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("color: #888;")
        item_layout.addWidget(time_label)
        
        content_text = QTextEdit()
        content_text.setPlainText(content)
        content_text.setReadOnly(True)
        content_text.setMaximumHeight(100)
        item_layout.addWidget(content_text)
        
        self.history_layout.insertWidget(0, item_widget)
        self.clipboard_history.insert(0, f"{timestamp}\n{content}")

    def save_history(self):
        filename = f"clipboard_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for item in self.clipboard_history:
                f.write(f"{item}\n\n")
        self.add_history_item(f"History saved to {filename}")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Clipboard Monitor",
            "Application minimized to system tray",
            QSystemTrayIcon.Information,
            2000
        )

def main():
    app = QApplication(sys.argv)
    ex = ClipboardMonitor()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()