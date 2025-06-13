import sys
import random
import string
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QSizePolicy, QCheckBox, QSpacerItem, QMainWindow, QScrollArea,
    QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class PasswordGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Generator")
        self.setMinimumSize(320, 360)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #6b7280;
                font-family: "Segoe UI", sans-serif;
            }
            QLabel#headline {
                color: #000000;
                font-weight: 700;
                font-size: 48px;
            }
            QLabel#subtext {
                font-weight: 400;
                font-size: 18px;
                margin-top: -10px;
                letter-spacing: 0.02em;
            }
            QLineEdit {
                border: 1.5px solid #4caf50;
                border-radius: 12px;
                padding: 14px 20px;
                font-size: 16px;
                color: #000000;
            }
            QPushButton#generateButton {
                background-color: #4caf50;
                border-radius: 12px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 18px;
                color: white;
                border: none;
                min-width: 140px;
            }
            QPushButton#generateButton:hover {
                background-color: #45a049;
            }
            QPushButton#copyButton {
                background-color: #000000;
                border-radius: 12px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 18px;
                color: #4caf50;
                border: 2px solid #4caf50;
                min-width: 140px;
            }
            QPushButton#copyButton:hover {
                background-color: #202020;
            }
            QLineEdit#passwordDisplay {
                border: 1.5px solid #000000;
                border-radius: 12px;
                padding: 14px 20px;
                font-size: 20px;
                font-weight: 600;
                color: #000000;
                background-color: #f9fff9;
            }
            QCheckBox {
                font-size: 16px;
                color: #4caf50;
                spacing: 12px;
            }
        """)

        self.initUI()

    def initUI(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)

        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(60, 40, 60, 40)
        self.main_layout.setSpacing(24)

        self.headline_label = QLabel("Generate a Strong Password")
        self.headline_label.setObjectName("headline")
        self.headline_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.headline_label, alignment=Qt.AlignLeft)

        self.subtext_label = QLabel("Specify the desired length and customize your password.")
        self.subtext_label.setObjectName("subtext")
        self.subtext_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.subtext_label, alignment=Qt.AlignLeft)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(20)

        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("Password Length (e.g. 12)")
        self.length_input.setFixedWidth(160)
        input_layout.addWidget(self.length_input, alignment=Qt.AlignLeft)

        self.generate_button = QPushButton("Generate")
        self.generate_button.setObjectName("generateButton")
        self.generate_button.clicked.connect(self.generate_password)
        input_layout.addWidget(self.generate_button, alignment=Qt.AlignLeft)

        self.main_layout.addLayout(input_layout)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(40)

        self.uppercase_cb = QCheckBox("Include Uppercase (A-Z)")
        self.uppercase_cb.setChecked(True)
        options_layout.addWidget(self.uppercase_cb)

        self.numbers_cb = QCheckBox("Include Numbers (0-9)")
        self.numbers_cb.setChecked(True)
        options_layout.addWidget(self.numbers_cb)

        self.symbols_cb = QCheckBox("Include Symbols (!@#$%)")
        self.symbols_cb.setChecked(True)
        options_layout.addWidget(self.symbols_cb)

        self.main_layout.addLayout(options_layout)

        output_layout = QHBoxLayout()
        output_layout.setSpacing(20)

        self.password_display = QLineEdit()
        self.password_display.setObjectName("passwordDisplay")
        self.password_display.setReadOnly(True)
        self.password_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        output_layout.addWidget(self.password_display)

        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        output_layout.addWidget(self.copy_button)

        self.main_layout.addLayout(output_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)

    def generate_password(self):
        length_text = self.length_input.text().strip()
        if not length_text.isdigit():
            self.password_display.setText("Please enter a valid positive integer.")
            return
        length = int(length_text)
        if length <= 0:
            self.password_display.setText("Length must be greater than zero.")
            return

        character_sets = [string.ascii_lowercase]
        if self.uppercase_cb.isChecked():
            character_sets.append(string.ascii_uppercase)
        if self.numbers_cb.isChecked():
            character_sets.append(string.digits)
        if self.symbols_cb.isChecked():
            character_sets.append(string.punctuation)
        if not character_sets:
            self.password_display.setText("Select at least one character set.")
            return

        all_chars = ''.join(character_sets)
        password = ''.join(random.choice(all_chars) for _ in range(length))
        self.password_display.setText(password)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password_display.text())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Generator")
        icon_path = os.path.join("assets", "lock.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(700, 480)
        self.password_generator = PasswordGenerator()
        self.setCentralWidget(self.password_generator)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
