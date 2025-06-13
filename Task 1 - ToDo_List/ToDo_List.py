import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QDialog,
    QLabel, QDateEdit, QTimeEdit, QComboBox, QMessageBox,
    QRadioButton, QButtonGroup, QGraphicsOpacityEffect
)
from PyQt5.QtCore import (
    Qt, QDate, QTime, QRect, QPropertyAnimation, pyqtSignal,
    QEasingCurve, QSize, QTimer
)
from PyQt5.QtGui import (
    QPalette, QColor, QFont, QPainter, QBrush, QPen, QMouseEvent, QIcon, QPixmap, QMovie
)

TASKS_FILE = "tasks.json"

class Task:
    def __init__(self, description, date, time, ringtone, category):
        self.description = description
        self.date = date
        self.time = time
        self.ringtone = ringtone
        self.category = category

    def __str__(self):
        return f"{self.description} — {self.date.toString('yyyy-MM-dd')} {self.time.toString('HH:mm')} [{self.ringtone}]"

    def to_dict(self):
        return {
            "description": self.description,
            "date": self.date.toString("yyyy-MM-dd"),
            "time": self.time.toString("HH:mm"),
            "ringtone": self.ringtone,
            "category": self.category
        }

    @staticmethod
    def from_dict(data):
        description = data.get("description", "")
        date_str = data.get("date", QDate.currentDate().toString("yyyy-MM-dd"))
        time_str = data.get("time", QTime.currentTime().toString("HH:mm"))
        ringtone = data.get("ringtone", "Chime")
        category = data.get("category", "Personal")

        date = QDate.fromString(date_str, "yyyy-MM-dd")
        if not date.isValid():
            date = QDate.currentDate()

        time = QTime.fromString(time_str, "HH:mm")
        if not time.isValid():
            time = QTime.currentTime()

        return Task(description, date, time, ringtone, category)

class SegmentedControl(QWidget):
    selectionChanged = pyqtSignal(str)

    def __init__(self, segments, parent=None):
        super().__init__(parent)
        self.segments = segments
        self.current_index = 0
        self.indicator_anim = QPropertyAnimation(self, b"dummy_property", self)
        self.indicator_anim.setDuration(250)
        self.indicator_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.setFixedHeight(36)
        self.setMinimumWidth(250)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self._dummy_property = 0

    @property
    def dummy_property(self):
        return self._dummy_property

    @dummy_property.setter
    def dummy_property(self, val):
        self._dummy_property = val

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        n = len(self.segments)

        segment_width = w / n
        radius = h / 2

        painter.setBrush(QColor("#d1d1d6"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, int(w-1), int(h-1), radius, radius)

        indicator_x = self.current_index * segment_width
        painter.setBrush(QColor("#007aff"))
        painter.drawRoundedRect(int(indicator_x), 0, int(segment_width), h, radius, radius)

        for i, text in enumerate(self.segments):
            x = i * segment_width
            rect = QRect(int(x), 0, int(segment_width), h)
            if i == self.current_index:
                painter.setPen(QColor("white"))
            else:
                painter.setPen(QColor("#3a3a3c"))
            painter.drawText(rect, Qt.AlignCenter | Qt.AlignVCenter, text)

        painter.setPen(QPen(QColor("#a1a1a6"), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(0, 0, int(w-1), int(h-1), radius, radius)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            seg_width = self.width() / len(self.segments)
            index = int(x // seg_width)
            if index != self.current_index and 0 <= index < len(self.segments):
                self.setCurrentIndex(index)
        super().mouseReleaseEvent(event)

    def setCurrentIndex(self, index, emit_signal=True):
        if 0 <= index < len(self.segments) and index != self.current_index:
            self.current_index = index
            self.update()
            if emit_signal:
                self.selectionChanged.emit(self.segments[self.current_index])

    def sizeHint(self):
        return QSize(300, 36)

class AnimatedPushButton(QPushButton):
    def __init__(self, *args, animation_duration=150, icon=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_duration = animation_duration
        self.pressed.connect(self._animate_press)
        if icon:
            self.setText(f"{icon} " + self.text())
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("text-align: left; padding-left: 8px;")

    def _animate_press(self):
        self.anim = QPropertyAnimation(self, b"opacity")
        self.anim.setDuration(self.animation_duration)
        self.anim.setStartValue(1.0)
        self.anim.setKeyValueAt(0.5, 0.6)
        self.anim.setEndValue(1.0)
        self.anim.start()
        if not self.graphicsEffect():
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
        else:
            self.opacity_effect = self.graphicsEffect()
        self.anim.valueChanged.connect(self.opacity_effect.setOpacity)

class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task" if task is None else "Update Task")
        self.resize(420, 320)
        self.task = task

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Task Description"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Enter task description...")
        self.desc_edit.returnPressed.connect(self.accept)
        layout.addWidget(self.desc_edit)

        h_layout = QHBoxLayout()

        v_date = QVBoxLayout()
        v_date.addWidget(QLabel("Date"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        v_date.addWidget(self.date_edit)

        v_time = QVBoxLayout()
        v_time.addWidget(QLabel("Time"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        v_time.addWidget(self.time_edit)

        h_layout.addLayout(v_date)
        h_layout.addLayout(v_time)
        layout.addLayout(h_layout)

        layout.addWidget(QLabel("Ringtone"))
        self.ringtone_combo = QComboBox()
        self.ringtones = ["Chime", "Ripple", "Glass", "Bell", "Digital"]
        self.ringtone_combo.addItems(self.ringtones)
        layout.addWidget(self.ringtone_combo)

        layout.addWidget(QLabel("Category"))
        self.category_group = QButtonGroup()
        category_layout = QHBoxLayout()
        self.personal_radio = QRadioButton("Personal")
        self.business_radio = QRadioButton("Business")
        self.category_group.addButton(self.personal_radio)
        self.category_group.addButton(self.business_radio)
        category_layout.addWidget(self.personal_radio)
        category_layout.addWidget(self.business_radio)
        layout.addLayout(category_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        if task:
            self.desc_edit.setText(task.description)
            self.date_edit.setDate(task.date)
            self.time_edit.setTime(task.time)
            index = self.ringtones.index(task.ringtone) if task.ringtone in self.ringtones else 0
            self.ringtone_combo.setCurrentIndex(index)
            if task.category == "Personal":
                self.personal_radio.setChecked(True)
            elif task.category == "Business":
                self.business_radio.setChecked(True)
            else:
                self.personal_radio.setChecked(True)
        else:
            self.personal_radio.setChecked(True)

    def get_task(self):
        description = self.desc_edit.text().strip()
        date = self.date_edit.date()
        time = self.time_edit.time()
        ringtone = self.ringtone_combo.currentText()
        if self.personal_radio.isChecked():
            category = "Personal"
        else:
            category = "Business"
        return Task(description, date, time, ringtone, category)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        icon_path = "assets/note.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(900, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.v_layout = QVBoxLayout(self.central_widget)
        self.v_layout.setContentsMargins(24, 24, 24, 24)
        self.v_layout.setSpacing(16)

        self.top_bar = QHBoxLayout()
        self.top_bar.setSpacing(15)

        self.segmented_switch = SegmentedControl(["All", "Personal", "Business"])
        self.segmented_switch.selectionChanged.connect(self.on_segment_changed)
        self.v_layout.addWidget(QLabel("TASKS"), alignment=Qt.AlignLeft)
        self.top_bar.addWidget(self.segmented_switch)
        self.top_bar.addStretch()

        self.search_icon_label = QLabel()
        self.search_icon_label.setFixedWidth(24)
        self.search_icon_label.setAlignment(Qt.AlignCenter)

        search_icon_path = "assets/search2.png"
        if os.path.exists(search_icon_path):
            search_pixmap = QPixmap(search_icon_path)
            search_pixmap = search_pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.search_icon_label.setPixmap(search_pixmap)

        self.top_bar.addWidget(self.search_icon_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tasks...")
        self.search_box.setFixedWidth(280)
        self.search_box.returnPressed.connect(self.filter_task_list)
        self.search_box.textChanged.connect(self.filter_task_list)
        self.top_bar.addWidget(self.search_box)
        self.top_bar.addSpacing(10)

        self.v_layout.addLayout(self.top_bar)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border-radius: 12px;
                padding: 12px;
                font-size: 18px;
                font-weight: 500;
                color: #333;
            }
            QListWidget::item {
                background: #fefefe;
                border-radius: 12px;
                margin: 8px 0;
                padding: 20px 24px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
                transition: background-color 0.3s ease;
            }
            QListWidget::item:selected {
                background: #007aff;
                color: white;
                box-shadow: 0 6px 14px rgba(0, 122, 255, 0.75);
            }
        """)
        self.v_layout.addWidget(self.task_list, 1)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(26)

        add_icon_path = "assets/add.png"
        add_icon = QIcon(add_icon_path) if os.path.exists(add_icon_path) else QIcon()
        self.add_btn = AnimatedPushButton("Add")
        self.add_btn.setIcon(add_icon)
        self.add_btn.setIconSize(QSize(24, 24))
        self.add_btn.setFixedHeight(44)
        self.add_btn.clicked.connect(self.add_task)
        self.buttons_layout.addWidget(self.add_btn)

        edit_icon_path = "assets/edit.png"
        edit_icon = QIcon(edit_icon_path) if os.path.exists(edit_icon_path) else QIcon()
        self.update_btn = AnimatedPushButton("Edit")
        self.update_btn.setIcon(edit_icon)
        self.update_btn.setIconSize(QSize(24, 24))
        self.update_btn.setFixedHeight(44)
        self.update_btn.clicked.connect(self.update_task)
        self.buttons_layout.addWidget(self.update_btn)

        delete_icon_path = "assets/delete.png"
        delete_icon = QIcon(delete_icon_path) if os.path.exists(delete_icon_path) else QIcon()
        self.delete_btn = AnimatedPushButton("Delete")
        self.delete_btn.setIcon(delete_icon)
        self.delete_btn.setIconSize(QSize(24, 24))
        self.delete_btn.setFixedHeight(44)
        self.delete_btn.clicked.connect(self.delete_task)
        self.buttons_layout.addWidget(self.delete_btn)

        self.v_layout.addLayout(self.buttons_layout)

        self.tasks = []
        self.current_category = "All"
        self.dark_mode = False

        self.load_tasks()
        self.apply_light_mode()
        self.refresh_task_list()

    def on_segment_changed(self, text):
        self.current_category = text
        self.refresh_task_list()

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_task = dialog.get_task()
            if not new_task.description:
                QMessageBox.warning(self, "Invalid Input", "Task description cannot be empty.")
                return
            self.tasks.append(new_task)
            self.save_tasks()
            self.refresh_task_list()

    def update_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to update.")
            return
        selected_index = self.task_list.row(selected_items[0])
        filtered_tasks = self.get_filtered_tasks()
        task_to_update = filtered_tasks[selected_index]

        dialog = TaskDialog(self, task_to_update)
        if dialog.exec_() == QDialog.Accepted:
            updated_task = dialog.get_task()
            if not updated_task.description:
                QMessageBox.warning(self, "Invalid Input", "Task description cannot be empty.")
                return
            idx = self.tasks.index(task_to_update)
            self.tasks[idx] = updated_task
            self.save_tasks()
            self.refresh_task_list()

    def delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a task to delete.")
            return
        selected_index = self.task_list.row(selected_items[0])
        filtered_tasks = self.get_filtered_tasks()
        task_to_delete = filtered_tasks[selected_index]
        self.tasks.remove(task_to_delete)
        self.save_tasks()
        self.refresh_task_list()

    def refresh_task_list(self):
        self.task_list.clear()
        filtered_tasks = self.get_filtered_tasks()
        for task in filtered_tasks:
            item = QListWidgetItem(str(task))
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.task_list.addItem(item)

    def get_filtered_tasks(self):
        search_text = self.search_box.text().strip().lower()
        if self.current_category == "All":
            filtered = self.tasks
        else:
            filtered = [t for t in self.tasks if t.category == self.current_category]
        if search_text:
            filtered = [t for t in filtered if search_text in t.description.lower()]
        return filtered

    def filter_task_list(self):
        self.refresh_task_list()

    def save_tasks(self):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                data = [task.to_dict() for task in self.tasks]
                json.dump(data, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Error saving tasks: {e}")

    def load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            return
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data_list = json.load(f)
                self.tasks = []
                for data in data_list:
                    task = Task.from_dict(data)
                    self.tasks.append(task)
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Error loading tasks: {e}")

    def apply_light_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QPushButton {
                background-color: #e4e4e8;
                border: none;
                padding: 10px 18px;
                border-radius: 14px;
                font-size: 14.5px;
                color: #222;
                font-weight: 600;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #dcdce3;
            }
            QPushButton:checked {
                background-color: #007aff;
                color: white;
            }
            QPushButton:pressed {
                background-color: #005fcc;
            }
            QLineEdit {
                background-color: white;
                border: 1.5px solid #bbb;
                border-radius: 14px;
                padding: 8px 12px;
                font-size: 15px;
                color: #333;
                transition: border-color 0.3s ease;
            }
            QLineEdit:focus {
                border-color: #007aff;
            }
            QLabel {
                color: #444;
            }
        """)
        palette = QApplication.style().standardPalette()
        palette.setColor(QPalette.WindowText, QColor("#222"))
        QApplication.setPalette(palette)

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1c1c1e;
            }
            QPushButton {
                background-color: #39393d;
                border: none;
                padding: 10px 18px;
                border-radius: 14px;
                font-size: 14.5px;
                color : #ddd;
                font-weight: 600;
                transition: background-color 0.3s ease;
            }
 QPushButton:hover {
                background-color: #505055;
            }
            QPushButton:checked {
                background-color: #0a84ff;
                color: white;
            }
            QPushButton:pressed {
                background-color: #0066ff;
            }
            QLineEdit {
                background-color: #2c2c2e;
                border: 1.5px solid #555;
                border-radius: 14px;
                padding: 8px 12px;
                font-size: 15px;
                color: #eee;
                transition: border-color 0.3s ease;
            }
            QLineEdit:focus {
                border-color: #0a84ff;
            }
            QLabel {
                color: #bbb;
            }
        """)
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(28, 28, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.Base, QColor(44, 44, 46))
        dark_palette.setColor(QPalette.AlternateBase, QColor(60, 60, 64))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        dark_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.Button, QColor(57, 57, 61))
        dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(10, 132, 255))
        dark_palette.setColor(QPalette.Highlight, QColor(10, 132, 255))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.setPalette(dark_palette)

def main():
    app = QApplication(sys.argv)

    splash_label = QLabel()
    splash_label.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    splash_label.setAttribute(Qt.WA_TranslucentBackground)
    splash_label.setAlignment(Qt.AlignCenter)

    gif_path = "assets/intro2.gif"
    if os.path.exists(gif_path):
        splash_movie = QMovie(gif_path)
        splash_label.setMovie(splash_movie)
        splash_movie.start()
        splash_label.resize(splash_movie.frameRect().size())
    else:
        splash_pixmap = QPixmap(400, 400)
        splash_pixmap.fill(QColor("#007aff"))
        splash_label.setPixmap(splash_pixmap)
        splash_label.resize(300, 300)

    splash_label.show()
    app.processEvents()

    def show_main():
        splash_label.close()
        window = MainWindow()
        window.show()
        app.main_window = window

    QTimer.singleShot(2000, show_main)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()