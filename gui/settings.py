from PyQt5.QtWidgets import QDialog, QSlider, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os
from config.config import save_config_options, load_config_options

# Пути к основным директориям и файлам
minecraft_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'game')

class Settings(QDialog):
    closed = pyqtSignal()  # Сигнал, отправляемый при закрытии окна

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        self.setWindowTitle("Настройки")
        self.setFixedSize(700, 500)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'launcher_icon.ico')))
        self.setStyleSheet("""
            QDialog {
                background-image: url('assets/background_settings.png');
                background-repeat: no-repeat;
                background-attachment: fixed;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                padding: 5px;
                min-width: 60px;
                min-height: 20px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.setWindowModality(Qt.ApplicationModal)

        self.memory_label = QLabel("Выделяемая ОЗУ:", self)
        self.memory_label.setStyleSheet("color: white; font-size: 20px")
        self.memory_label.setGeometry(70, 120, 280, 50)

        self.memory_value_label = QLabel(self)
        self.memory_value_label.setStyleSheet("color: white; font-size: 20px")
        self.memory_value_label.setGeometry(260, 120, 280, 50)

        self.memory_slider = QSlider(Qt.Horizontal, self)
        self.memory_slider.setRange(2, 16)
        self.memory_slider.setSingleStep(1)
        self.memory_slider.setPageStep(1)
        self.memory_slider.setTickInterval(1)
        self.memory_slider.setTickPosition(QSlider.TicksBelow)
        self.memory_slider.setGeometry(70, 190, 560, 50)
        self.memory_slider.valueChanged.connect(self.update_memory_value)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(210, 300, 250, 50)
        self.save_button.clicked.connect(self.save_config)
        self.save_button.setStyleSheet(
            "QPushButton {"
            "background-color: rgba(0, 0, 0, 128);"
            "border-radius: 10px;"
            "font-size: 30px;"
            "text-align: center;"
            "color: white;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(0, 255, 60, 128);"
            "border-radius: 10px;"
            "font-size: 32px;"
            "text-align: center;"
            "color: white;"
            "}"
            "QPushButton:pressed {"
            "background-color: rgba(0, 255, 180, 128);"
            "border-radius: 10px;"
            "font-size: 30px;"
            "text-align: center;"
            "color: white;"
            "}"
        )

    def load_config(self):
        """Загружает конфигурацию из файла и применяет её к интерфейсу."""
        self.config = load_config_options()
        saved_memory = self.config.get('allocated_memory', 4)
        self.memory_slider.setValue(saved_memory)
        self.update_memory_value(saved_memory)

    def update_memory_value(self, value):
        """Обновляет значение выделяемой памяти."""
        self.memory_value_label.setText(f"{value} ГБ")

    def save_config(self):
        """Сохраняет текущие настройки в файл конфигурации."""
        allocated_memory = self.memory_slider.value()
        self.config['allocated_memory'] = allocated_memory
        save_config_options(self.config)
        self.close()

    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна, отправляя сигнал closed."""
        self.closed.emit()
        super().closeEvent(event)