import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel,
    QSizePolicy, QHBoxLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setWindowIcon(QIcon("asset\calculator.png"))
        self.resize(460, 700)
        self.setMinimumSize(320, 600)
        self.initUI()
        self.reset()

    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        self.setLayout(main_layout)

        self.calc_panel = QVBoxLayout()
        self.calc_panel.setSpacing(20)
        main_layout.addLayout(self.calc_panel, stretch=3)

        self.display = QLabel("0", self)
        self.display.setFixedHeight(120)
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        self.display.setStyleSheet("""
            background-color: #f0f0f3;
            color: #000000;
            border-radius: 12px;
            padding: 0 24px;
            box-shadow: inset 5px 5px 8px #d1d1d6,
                        inset -5px -5px 8px #ffffff;
        """)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.calc_panel.addWidget(self.display)

        self.buttons_layout = QGridLayout()
        self.buttons_layout.setSpacing(16)
        self.calc_panel.addLayout(self.buttons_layout)

        self.btns = [
            ("AC", 0, 0, 1, 1, "func"),
            ("+/-", 0, 1, 1, 1, "func"),
            ("%", 0, 2, 1, 1, "func"),
            ("/", 0, 3, 1, 1, "op"),
            ("7", 1, 0, 1, 1, "num"),
            ("8", 1, 1, 1, 1, "num"),
            ("9", 1, 2, 1, 1, "num"),
            ("×", 1, 3, 1, 1, "op"),
            ("4", 2, 0, 1, 1, "num"),
            ("5", 2, 1, 1, 1, "num"),
            ("6", 2, 2, 1, 1, "num"),
            ("−", 2, 3, 1, 1, "op"),
            ("1", 3, 0, 1, 1, "num"),
            ("2", 3, 1, 1, 1, "num"),
            ("3", 3, 2, 1, 1, "num"),
            ("+", 3, 3, 1, 1, "op"),
            ("0", 4, 0, 1, 2, "num"),
            (".", 4, 2, 1, 1, "num"),
            ("=", 4, 3, 1, 1, "op"),
        ]

        self.buttons = {}

        def base_button_style():
            return """
                QPushButton {
                    border-radius: 24px;
                    font-size: 32px;
                    font-family: 'Segoe UI', sans-serif;
                    padding: 0px;
                    min-width: 70px;
                    min-height: 70px;
                    box-shadow: 4px 4px 8px #d1d1d6,
                                -4px -4px 8px #ffffff;
                }
                QPushButton:pressed {
                    box-shadow: inset 4px 4px 6px #d1d1d6,
                                inset -4px -4px 6px #ffffff;
                }
            """

        def func_style():
            return base_button_style() + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d6d6d6, stop:1 #f0f0f3);
                    color: #6b7280;
                    border: 1.5px solid #b0b0b0;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #babebe, stop:1 #e1e2e5);
                    border: 1.5px solid #8a8a8a;
                }
            """

        def num_style():
            return base_button_style() + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #eeeeee, stop:1 #d3d3d3);
                    color: #000000;
                    border: 1.5px solid #b2b2b2;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dcdcdc, stop:1 #c0c0c0);
                    border: 1.5px solid #999999;
                }
            """

        def op_style():
            return base_button_style() + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffb347, stop:1 #ff9500);
                    color: white;
                    border: 1.5px solid #e07b00;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e08600, stop:1 #cc7800);
                    border: 1.5px solid #a66500;
                }
            """

        for text, r, c, rowspan, colspan, ctype in self.btns:
            btn = QPushButton(text, self)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            if ctype == "func":
                btn.setStyleSheet(func_style())
            elif ctype == "num":
                btn.setStyleSheet(num_style())
            elif ctype == "op":
                btn.setStyleSheet(op_style())
            btn.clicked.connect(self.on_button_clicked)
            self.buttons_layout.addWidget(btn, r, c, rowspan, colspan)
            self.buttons[text] = btn

        self.history_panel = QListWidget()
        self.history_panel.setMaximumWidth(240)
        self.history_panel.setStyleSheet("""
            QListWidget {
                background: #f9fafb;
                border-radius: 12px;
                padding: 12px;
                font-size: 18px;
                color: #6b7280;
                border: 1.5px solid #e5e7eb;
            }
        """)
        main_layout.addWidget(self.history_panel, stretch=2)

    def reset(self):
        self.current_value = "0"
        self.pending_value = None
        self.pending_operator = None
        self.last_button_was_op = False
        self.just_evaluated = False
        self.update_display()
        self.buttons["AC"].setText("AC")
        self.history_panel.clear()

    def update_display(self):
        max_len = 15
        text = self.current_value
        if len(text) > max_len:
            try:
                val = float(text)
                text = "{:.6e}".format(val)
            except:
                text = text[:max_len]
        self.display.setText(text)
        if self.current_value == "0" and not self.pending_operator:
            self.buttons["AC"].setText("AC")
        else:
            self.buttons["AC"].setText("C")

    def on_button_clicked(self):
        sender = self.sender()
        text = sender.text()
        if text in "0123456789":
            self.input_digit(text)
        elif text == ".":
            self.input_decimal()
        elif text in ["+", "−", "×", "/"]:
            self.input_operator(text)
        elif text == "=":
            self.evaluate()
        elif text == "+/-":
            self.toggle_sign()
        elif text == "%":
            self.percent()
        elif text in ["AC", "C"]:
            self.clear()
        self.update_display()

    def input_digit(self, digit):
        if self.just_evaluated:
            self.current_value = digit
            self.just_evaluated = False
        elif self.current_value == "0" or self.last_button_was_op:
            self.current_value = digit
            self.last_button_was_op = False
        else:
            self.current_value += digit

    def input_decimal(self):
        if self.just_evaluated:
            self.current_value = "0."
            self.just_evaluated = False
        elif "." not in self.current_value:
            self.current_value += "."

    def input_operator(self, op):
        op_map = {"+": "+", "−": "-", "×": "*", "/": "/"}
        real_op = op_map.get(op, op)
        if self.pending_operator and not self.last_button_was_op:
            self.evaluate()
        try:
            self.pending_value = float(self.current_value)
        except:
            self.pending_value = 0.0
        self.pending_operator = real_op
        self.last_button_was_op = True
        self.just_evaluated = False

    def evaluate(self):
        if not self.pending_operator:
            return
        try:
            current = float(self.current_value)
            expression = f"{self.pending_value} {self.pending_operator} {current}"
            result = None
            if self.pending_operator == "+":
                result = self.pending_value + current
            elif self.pending_operator == "-":
                result = self.pending_value - current
            elif self.pending_operator == "*":
                result = self.pending_value * current
            elif self.pending_operator == "/":
                if current == 0:
                    self.current_value = "Error"
                    self.pending_operator = None
                    self.pending_value = None
                    self.add_history(f"{expression} = Error (division by zero)")
                    return
                result = self.pending_value / current
            if result is not None:
                if result.is_integer():
                    result_str = str(int(result))
                else:
                    result_str = str(round(result, 9))
                self.add_history(f"{expression} = {result_str}")
                self.current_value = result_str
                self.pending_value = result
                self.pending_operator = None
                self.just_evaluated = True
                self.last_button_was_op = False
        except Exception as e:
            self.current_value = "Error"
            self.pending_operator = None
            self.pending_value = None
            self.just_evaluated = True
            self.add_history(f"Error: {str(e)}")

    def toggle_sign(self):
        try:
            if self.current_value == "0" or self.current_value == "Error":
                return
            val = float(self.current_value)
            val = -val
            if val.is_integer():
                self.current_value = str(int(val))
            else:
                self.current_value = str(val)
        except Exception:
            self.current_value = "Error"

    def percent(self):
        try:
            val = float(self.current_value)
            val /= 100.0
            if self.pending_value is not None and self.pending_operator:
                val = self.pending_value * val
            if val.is_integer():
                self.current_value = str(int(val))
            else:
                self.current_value = str(val)
        except Exception:
            self.current_value = "Error"

    def clear(self):
        if self.buttons["AC"].text() == "AC":
            self.reset()
        else:
            self.current_value = "0"
            self.update_display()
            self.last_button_was_op = False

    def add_history(self, entry):
        item = QListWidgetItem(entry)
        font = QFont("Segoe UI", 16)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignLeft)
        self.history_panel.addItem(item)
        self.history_panel.scrollToBottom()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor("#ffffff"))
    palette.setColor(QPalette.WindowText, QColor("#000000"))
    palette.setColor(QPalette.Base, QColor("#f9fafb"))
    palette.setColor(QPalette.Text, QColor("#000000"))
    app.setPalette(palette)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
