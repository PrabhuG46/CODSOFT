import sys
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QMessageBox, QPushButton, QGraphicsOpacityEffect, QFrame
)
from PyQt5.QtGui import QFont, QColor, QPalette, QCursor, QPixmap, QIcon, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QEasingCurve, QPropertyAnimation, QSize

PRIMARY_COLOR = "#2E86AB"
SECONDARY_COLOR = "#F2D7D5"

class ImageButton(QPushButton):
    def __init__(self, image_path, label_text, click_callback):
        super().__init__()
        self.image_path = image_path
        self.label_text = label_text
        self.click_callback = click_callback

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedSize(140, 180)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.init_ui()

        self.clicked.connect(self.on_click)

    def circularPixmap(self, pixmap: QPixmap, size: QSize) -> QPixmap:
        scaled = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        result = QPixmap(size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size.width(), size.height())
        painter.setClipPath(path)
        x_off = (size.width() - scaled.width()) // 2
        y_off = (size.height() - scaled.height()) // 2
        painter.drawPixmap(x_off, y_off, scaled)
        painter.end()
        return result

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignHCenter)

        self.image_label = QLabel()
        self.image_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.image_label.setStyleSheet("background: transparent;")
        pixmap = QPixmap(self.image_path)
        circle_size = QSize(100, 100)
        circular_pixmap = self.circularPixmap(pixmap, circle_size)
        self.image_label.setPixmap(circular_pixmap)
        self.image_label.setFixedSize(circle_size)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.text_label = QLabel(self.label_text)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Medium))
        self.text_label.setStyleSheet(f"color: {PRIMARY_COLOR}; background: transparent;")
        self.text_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        layout.addWidget(self.image_label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.text_label, alignment=Qt.AlignHCenter)

        self.setLayout(layout)

        self.setFlat(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.03);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.06);
            }
        """)

    def on_click(self):
        self.animate_click()
        if callable(self.click_callback):
            self.click_callback()

    def animate_click(self):
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(220)
        anim.setStartValue(1.0)
        anim.setKeyValueAt(0.5, 0.6)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        self.anim = anim

class RockPaperScissorsGame(QWidget):
    def __init__(self):
        super().__init__()

        self.user_score = 0
        self.computer_score = 0

        self.setMinimumSize(600, 450)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {SECONDARY_COLOR};
                font-family: 'Segoe UI', sans-serif;
                color: {PRIMARY_COLOR};
            }}
            QLabel#headline {{
                color: {PRIMARY_COLOR};
                font-weight: 700;
                font-size: 48px;
                margin-bottom: 4px;
                background-color: transparent; /* Remove background color */
            }}
            QMessageBox QLabel {{
                font-size: 18px;
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 48, 60, 60)
        main_layout.setSpacing(12)

        self.headline = QLabel("Start Playing!")
        self.headline.setObjectName("headline")
        main_layout.addWidget(self.headline, alignment=Qt.AlignLeft)

        # Score Frame
        self.score_frame = QFrame()
        self.score_frame.setFrameShape(QFrame.Box)
        self.score_frame.setFrameShadow(QFrame.Plain)  # Changed to Plain to remove the sunken effect
        self.score_frame.setStyleSheet(f"background-color: {PRIMARY_COLOR}; border: 2px solid {PRIMARY_COLOR}; border-radius: 8px;") # border color same as background
        score_layout = QVBoxLayout()
        score_layout.setContentsMargins(12, 12, 12, 12)

        self.score_label = QLabel(f"Score  You: {self.user_score}   Computer: {self.computer_score}")
        self.score_label.setObjectName("scoreLabel")
        self.score_label.setFont(QFont("Segoe UI", 24, QFont.Weight.DemiBold))
        self.score_label.setStyleSheet(f"color: {SECONDARY_COLOR};")
        self.score_label.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(self.score_label)

        self.score_frame.setLayout(score_layout)
        main_layout.addWidget(self.score_frame)

        emoji_layout = QHBoxLayout()
        emoji_layout.setSpacing(48)

        assets_dir = "assets"
        rock_path = os.path.join(assets_dir, "rock.png")
        paper_path = os.path.join(assets_dir, "paper.png")
        scissors_path = os.path.join(assets_dir, "scissors.png")

        self.rock_btn = ImageButton(rock_path, "Rock", lambda: self.play("rock"))
        emoji_layout.addWidget(self.rock_btn)

        self.paper_btn = ImageButton(paper_path, "Paper", lambda: self.play("paper"))
        emoji_layout.addWidget(self.paper_btn)

        self.scissors_btn = ImageButton(scissors_path, "Scissors", lambda: self.play("scissors"))
        emoji_layout.addWidget(self.scissors_btn)

        main_layout.addLayout(emoji_layout)

        self.setLayout(main_layout)

    def play(self, user_choice):
        computer_choice = random.choice(["rock", "paper", "scissors"])
        result = self.determine_winner(user_choice, computer_choice)

        if result == "win":
            self.user_score += 1
            message = "You win!"
        elif result == "lose":
            self.computer_score += 1
            message = "You lose!"
        else:
            message = "It's a tie!"

        self.show_result(user_choice, computer_choice, message)
        self.score_label.setText(f"Score  You: {self.user_score}   Computer: {self.computer_score}")

    def determine_winner(self, user_choice, computer_choice):
        if user_choice == computer_choice:
            return "tie"
        elif (user_choice == "rock" and computer_choice == "scissors") or \
             (user_choice == "paper" and computer_choice == "rock") or \
             (user_choice == "scissors" and computer_choice == "paper"):
            return "win"
        else:
            return "lose"

    def show_result(self, user_choice, computer_choice, message):
        result_text = f"<b>You chose:</b> {user_choice.capitalize()}<br>" \
                      f"<b>Computer chose:</b> {computer_choice.capitalize()}<br><br>" \
                      f"<strong>{message}</strong>"
        QMessageBox.information(self, "Game Result", result_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rock-Paper-Scissors")
        self.setMinimumSize(640, 480)
        self.setup_ui()

    def setup_ui(self):
        self.game_widget = RockPaperScissorsGame()
        self.setCentralWidget(self.game_widget)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        self.setPalette(palette)

        app_icon_path = os.path.join("assets", "app_icon.png")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        else:
            print(f"Icon file not found: {app_icon_path}")

def main():
    app = QApplication(sys.argv)
    app_icon_path = os.path.join("assets", "app_icon.png")
    if os.path.exists(app_icon_path):
        app_icon = QIcon(app_icon_path)
        app.setWindowIcon(app_icon)
    else:
        print(f"Icon file not found: {app_icon_path}")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
