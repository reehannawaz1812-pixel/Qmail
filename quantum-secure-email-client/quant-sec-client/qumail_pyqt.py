import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit, 
                             QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QSplitter, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

import gui_backend

# --- Theme & Styles ---
STYLE_SHEET = """
QMainWindow {
    background-color: #1e1e2e;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QLineEdit, QTextEdit, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px;
    color: #cdd6f4;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton#btn_logout {
    background-color: #f38ba8;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 10px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QTableWidget {
    background-color: #313244;
    border: 1px solid #45475a;
    gridline-color: #45475a;
}
QHeaderView::section {
    background-color: #181825;
    padding: 5px;
    border: none;
    color: #cdd6f4;
}
"""

class WorkerThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
    def run(self):
        res = self.func(*self.args)
        self.finished.emit(res)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Login")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet(STYLE_SHEET)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
        # Logo / Title
        title = QLabel("QuMail")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #89b4fa;")
        layout.addWidget(title)
        
        subtitle = QLabel("Quantum Secure Communication")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Form
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (Gmail/Yahoo)")
        layout.addWidget(self.email_input)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("App Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)
        
        layout.addSpacing(20)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color: #f38ba8;")
        layout.addWidget(self.status_lbl)

    def handle_login(self):
        email = self.email_input.text()
        pwd = self.pass_input.text()
        
        if not email or not pwd:
            self.status_lbl.setText("All fields required")
            return
            
        self.status_lbl.setText("Authenticating...")
        self.status_lbl.setStyleSheet("color: #f9e2af;")
        
        # Use Thread
        self.worker = WorkerThread(gui_backend.login, email, pwd)
        self.worker.finished.connect(self.on_login_finished)
        self.worker.start()
        
    def on_login_finished(self, res):
        if res["success"]:
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            self.status_lbl.setText(f"Error: {res['message']}")
            self.status_lbl.setStyleSheet("color: #f38ba8;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Header
        header = QHBoxLayout()
        logo = QLabel("QuMail")
        logo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(logo)
        
        header.addStretch()
        
        user_lbl = QLabel(f"User: {gui_backend.session.username}")
        header.addWidget(user_lbl)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("btn_logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        header.addWidget(logout_btn)
        
        main_layout.addLayout(header)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.init_inbox_tab()
        self.init_compose_tab()
        self.init_key_manager_tab()
        self.init_blockchain_tab()
        self.init_settings_tab()
        
    def logout(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()

    # --- Inbox ---
    def init_inbox_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Sidebar List
        left_layout = QVBoxLayout()
        
        refresh_btn = QPushButton("Sync Inbox")
        refresh_btn.clicked.connect(self.refresh_inbox)
        left_layout.addWidget(refresh_btn)
        
        self.email_list = QTableWidget()
        self.email_list.setColumnCount(3)
        self.email_list.setHorizontalHeaderLabels(["From", "Subject", "Date"])
        self.email_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.email_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.email_list.setSelectionMode(QTableWidget.SingleSelection)
        self.email_list.itemClicked.connect(self.display_email)
        left_layout.addWidget(self.email_list)
        
        layout.addLayout(left_layout, 1)
        
        # Preview Pane
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("Select an email to read decrypted content...")
        layout.addWidget(self.preview_area, 2)
        
        self.tabs.addTab(tab, "Inbox")
        
        # Initial Load
        self.refresh_inbox()

    def refresh_inbox(self):
        self.worker = WorkerThread(gui_backend.fetch_inbox)
        self.worker.finished.connect(self.populate_inbox)
        self.worker.start()
        
    def populate_inbox(self, res):
        if res["success"]:
            self.emails_data = res["emails"]
            self.email_list.setRowCount(len(self.emails_data))
            for i, em in enumerate(self.emails_data):
                self.email_list.setItem(i, 0, QTableWidgetItem(em['sender']))
                self.email_list.setItem(i, 1, QTableWidgetItem(em['subject']))
                self.email_list.setItem(i, 2, QTableWidgetItem(em['date']))
        else:
            QMessageBox.warning(self, "Sync Error", res["message"])

    def display_email(self, item):
        row = item.row()
        email = self.emails_data[row]
        body = email['body']
        
        display_text = f"<b style='font-size: 18px;'>FROM:</b> {email['sender']}<br>"
        display_text += f"<b style='font-size: 18px;'>SUBJECT:</b> {email['subject']}<br>"
        display_text += f"<b style='font-size: 14px; color: #94e2d5;'>DATE:</b> {email['date']}<br><br>"
        display_text += "<hr style='border: 1px solid #45475a;'><br>"

        # Check if the message is a Quantum Payload
        try:
            payload = json.loads(body)
            if isinstance(payload, dict) and "level" in payload:
                level = payload.get("level")
                display_text += "<div style='background-color: #313244; padding: 15px; border-radius: 10px; border: 1px solid #89b4fa;'>"
                display_text += f"<h3 style='color: #89b4fa; margin-top: 0;'>🛡️ QUANTUM SECURITY REPORT</h3>"
                display_text += f"<b>Security Level:</b> Level {level} ({self.get_level_name(level)})<br>"
                display_text += f"<b>Encryption Protocol:</b> {self.get_protocol_name(level)}<br>"
                display_text += f"<b>Status:</b> <span style='color: #a6e3a1;'>Decrypted Successfully via local Key Manager</span><br><br>"
                
                display_text += "<b style='color: #f38ba8;'>RAW ENCRYPTED PAYLOAD (Intercepted):</b><br>"
                display_text += f"<code style='color: #fab387;'>{body[:200]}...</code><br><br>"
                
                display_text += "<b>DECRYPTED MESSAGE:</b><br>"
                # In Level 3 simulation, we display the original message if we could "fetch" the key
                # For demo, we assume the simulator provided the key
                decrypted_msg = self.simulate_decryption(payload)
                display_text += f"<div style='color: #cdd6f4; font-size: 16px; margin-top: 10px;'>{decrypted_msg}</div>"
                display_text += "</div>"
            else:
                display_text += f"<div style='font-size: 16px;'>{body}</div>"
        except:
            # Plain text email
            display_text += f"<div style='font-size: 16px;'>{body}</div>"

        self.preview_area.setHtml(display_text)

    def get_level_name(self, level):
        levels = {1: "Standard", 2: "Post-Quantum", 3: "Quantum Key Advanced"}
        return levels.get(level, "Unknown")

    def get_protocol_name(self, level):
        protocols = {1: "RSA-AES Hybrid", 2: "CRYSTALS-Kyber", 3: "QKD (One-Time Pad Simulation)"}
        return protocols.get(level, "N/A")

    def simulate_decryption(self, payload):
        # Call backend to perform real decryption of the demo payload
        return gui_backend.decrypt_payload(payload)

    # --- Compose ---
    def init_compose_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(50, 20, 50, 20)
        
        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText("Recipient Email")
        form_layout.addWidget(QLabel("To:"))
        form_layout.addWidget(self.to_input)
        
        self.sub_input = QLineEdit()
        self.sub_input.setPlaceholderText("Subject")
        form_layout.addWidget(QLabel("Subject:"))
        form_layout.addWidget(self.sub_input)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems([
            "Level 1: Standard Encryption (RSA-AES)",
            "Level 2: Post-Quantum Cryptography (Kyber-AES)",
            "Level 3: Quantum Key Advanced (QKD)"
        ])
        self.level_combo.setCurrentIndex(2)
        form_layout.addWidget(QLabel("Security Level:"))
        form_layout.addWidget(self.level_combo)
        
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Write your secure message here...")
        form_layout.addWidget(QLabel("Message:"))
        form_layout.addWidget(self.body_input)
        
        send_btn = QPushButton("Send Quantum Mail")
        send_btn.clicked.connect(self.send_mail)
        send_btn.setFixedHeight(40)
        form_layout.addWidget(send_btn)
        
        layout.addLayout(form_layout)
        self.tabs.addTab(tab, "Compose")

    def send_mail(self):
        to = self.to_input.text()
        sub = self.sub_input.text()
        body = self.body_input.toPlainText()
        level_idx = self.level_combo.currentIndex() + 1 # 1, 2, 3
        
        if not to or not sub:
            QMessageBox.warning(self, "Error", "Recipient and Subject required")
            return
            
        self.worker = WorkerThread(gui_backend.send_email, to, sub, body, level_idx)
        self.worker.finished.connect(self.on_send_finished)
        self.worker.start()
        
    def on_send_finished(self, res):
        if res["success"]:
            QMessageBox.information(self, "Success", res["message"])
            self.to_input.clear()
            self.sub_input.clear()
            self.body_input.clear()
            self.refresh_blockchain() # Update log
        else:
            QMessageBox.critical(self, "Error", res["message"])

    # --- Key Manager ---
    def init_key_manager_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Quantum Key Manager (API-Based)")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        self.km_log = QTextEdit()
        self.km_log.setReadOnly(True)
        self.km_log.setStyleSheet("font-family: Courier; color: #a6e3a1;")
        layout.addWidget(self.km_log)
        
        btn_sim = QPushButton("Simulate QKD Key Generation")
        btn_sim.clicked.connect(self.simulate_qkd)
        layout.addWidget(btn_sim)
        
        self.tabs.addTab(tab, "Key Manager")

    def simulate_qkd(self):
        self.km_log.append("> Connecting to Quantum Simulator...")
        # Simulate delay
        QTimer.singleShot(500, self._run_sim)
        
    def _run_sim(self):
        try:
            k_bytes, k_str = gui_backend.session.quantum_sim.generate_key()
            self.km_log.append(f"> Qubits Measured: 16 (Repeated)")
            self.km_log.append(f"> Basis: Hadamard (Superposition)")
            self.km_log.append(f"> Generated High-Entropy Key: {k_str}")
            self.km_log.append(f"> Status: Key Cached for Session.")
            self.km_log.append("-" * 40)
        except Exception as e:
            self.km_log.append(f"> Error: {str(e)}")

    # --- Blockchain Log ---
    def init_blockchain_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Blockchain Audit Log")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        self.bc_table = QTableWidget()
        self.bc_table.setColumnCount(5)
        self.bc_table.setHorizontalHeaderLabels(["Idx", "Timestamp", "Sender", "Receiver", "Hash"])
        self.bc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.bc_table)
        
        refresh = QPushButton("Refresh Ledger")
        refresh.clicked.connect(self.refresh_blockchain)
        layout.addWidget(refresh)
        
        self.tabs.addTab(tab, "Blockchain Log")
        self.refresh_blockchain()

    def refresh_blockchain(self):
        chain = gui_backend.get_blockchain_data()
        self.bc_table.setRowCount(len(chain))
        for i, block in enumerate(chain):
            data = block['data']
            self.bc_table.setItem(i, 0, QTableWidgetItem(str(block['index'])))
            self.bc_table.setItem(i, 1, QTableWidgetItem(str(block['timestamp'])))
            self.bc_table.setItem(i, 2, QTableWidgetItem(data.get('sender', 'System')))
            self.bc_table.setItem(i, 3, QTableWidgetItem(data.get('receiver', 'N/A')))
            # Use the instance 'session' instead of the class 'Session'
            block_hash = gui_backend.session.blockchain.hash(block)
            self.bc_table.setItem(i, 4, QTableWidgetItem(block_hash[:16] + "..."))

    # --- Settings ---
    def init_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("UI Customization & Config (Coming Soon)"))
        self.tabs.addTab(tab, "Settings")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
