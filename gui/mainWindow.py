import os
import sys
import json
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton, QProgressBar, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from scripts.launchThread import LaunchThread
from gui.settings import Settings
from config.config import load_config, load_config_options
from scripts.serverLauncher import checkUpdateModpack, downloadUpdateModpack

# Пути к основным директориям и файлам
minecraft_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'game')
logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'minecraft_logo.png')
version = os.path.join(minecraft_directory, 'version.json')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_threads()
        self.load_configs()
        self.apply_config()

    def setup_ui(self):
        """Инициализирует пользовательский интерфейс."""
        self.setWindowTitle("Launcher")
        self.setFixedSize(1240, 680)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'launcher_icon.ico')))
        self.setStyleSheet("""
            QMainWindow {
                background-image: url('assets/background.png');
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

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.logo = QLabel(self.centralwidget)
        self.logo.setAlignment(Qt.AlignCenter)
        self.set_logo_icon(logo_path)
        self.logo.setGeometry(315, 70, 570, 150)

        self.username = QComboBox(self.centralwidget)
        self.username.setEditable(False)
        self.username.setStyleSheet("""
            QComboBox {
                font-size: 20px; 
                background-color: rgba(0, 0, 0, 128); 
                border: 1px solid #2C3E50; 
                border-radius: 5px; 
                padding: 5px; 
                color: white;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(0, 0, 0, 128);
                color: #ffffff;
                selection-background-color: rgba(120, 120, 120, 128);
            }
        """)
        self.username.setGeometry(400, 420, 250, 50)

        self.start_progress = QProgressBar(self.centralwidget)
        self.start_progress.setVisible(False)
        self.start_progress.setStyleSheet("""
            QProgressBar { 
                color: white; 
                border: 1px solid #2C3E50; 
                border-radius: 5px; 
                background-color: rgba(0, 0, 0, 220); 
            } 
            QProgressBar::chunk { 
                background-color: rgba(0, 255, 180, 160); 
            }
        """)
        self.start_progress.setGeometry(310, 500, 570, 30)

        self.start_button_vanilla = QPushButton(self.centralwidget)
        self.start_button_vanilla.setText('Играть')
        self.start_button_vanilla.setGeometry(400, 300, 370, 80)
        self.start_button_vanilla.setStyleSheet(
            "QPushButton {"
            "background-color: rgba(0, 0, 0, 128);"
            "border-radius: 10px;"
            "font-size: 34px;"
            "text-align: center;"
            "color: white;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(0, 255, 60, 128);"
            "border-radius: 10px;"
            "font-size: 36px;"
            "text-align: center;"
            "color: white;"
            "}"
            "QPushButton:pressed {"
            "background-color: rgba(0, 255, 180, 128);"
            "border-radius: 10px;"
            "font-size: 34px;"
            "text-align: center;"
            "color: white;"
            "}"
        )

        self.username_button = QPushButton(self.centralwidget)
        self.username_button.setText('✚')
        self.username_button.setStyleSheet(
            "QPushButton {"
            "background-color: rgba(0, 0, 0, 128);"
            "border-radius: 5px;"
            "font-size: 32px;"
            "text-align: center;"
            "color: white;"
            "border: 1px solid #2C3E50;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(120, 210, 127, 128);"
            "border-radius: 5px;"
            "font-size: 32px;"
            "text-align: center;"
            "color: white;"
            "border: 1px solid #2C3E50;"
            "}"
        )
        self.username_button.setGeometry(660, 420, 50, 50)
        self.username_button.clicked.connect(self.show_auth_window)

        self.open_folder = QPushButton(self.centralwidget)
        self.open_folder.setText('📁')
        self.open_folder.setStyleSheet(
            "QPushButton {"
            "background-color: rgba(0, 0, 0, 128);"
            "border-radius: 5px;"
            "font-size: 28px;"
            "text-align: center;"
            "color: white;"
            "border: 1px solid #2C3E50;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(120, 210, 127, 128);"
            "border-radius: 5px;"
            "font-size: 28px;"
            "text-align: center;"
            "color: white;"
            "border: 1px solid #2C3E50;"
            "}"
        )
        self.open_folder.setGeometry(720, 420, 50, 50)
        self.open_folder.clicked.connect(self.show_folder_minecraft)

        self.settings = QPushButton(self.centralwidget)
        self.settings.setText('⚙')
        self.settings.setGeometry(40, 600, 50, 50)
        self.settings.clicked.connect(self.show_settings_window)
        self.settings.setStyleSheet(
            "QPushButton {"
            "background-color: rgba(0, 0, 0, 0);"
            "border-radius: 10px;"
            "font-size: 40px;"
            "text-align: center;"
            "color: white;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(0, 255, 60, 0);"
            "border-radius: 10px;"
            "font-size: 42px;"
            "text-align: center;"
            "color: white;"
            "}"
            "QPushButton:pressed {"
            "background-color: rgba(0, 255, 180, 0);"
            "border-radius: 10px;"
            "font-size: 40px;"
            "text-align: center;"
            "color: white;"
            "}"
        )

        self.start_button_vanilla.clicked.connect(self.launch_game)

    def setup_threads(self):
        """Настраивает потоки для запуска игры."""
        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)
        self.launch_thread.game_launched_signal.connect(self.hide_launcher)
        self.launch_thread.game_closed_signal.connect(self.show_launcher)

    def load_configs(self):
        """Загружает конфигурационные файлы."""
        self.config = load_config()
        self.config_options = load_config_options()

    def hide_launcher(self):
        """Скрывает лаунчер при запуске игры."""
        self.hide()

    def show_launcher(self):
        """Отображает лаунчер после закрытия игры."""
        self.show()

    def show_auth_window(self):
        """Отображает окно авторизации."""
        from gui.auth import Auth
        if not hasattr(self, 'auth_window') or self.auth_window is None:
            self.auth_window = Auth(self)
            self.auth_window.closed.connect(self.on_auth_closed)
        self.auth_window.show()

    def on_auth_closed(self):
        """Обновляет конфигурацию после закрытия окна авторизации."""
        self.auth_window = None
        self.config = load_config()
        self.apply_config()

    def show_settings_window(self):
        """Отображает окно настроек."""
        if not hasattr(self, 'settings_window') or self.settings_window is None:
            self.settings_window = Settings(self)
            self.settings_window.closed.connect(self.on_settings_closed)
        self.settings_window.show()

    def on_settings_closed(self):
        """Отображает лаунчер после закрытия окна настроек."""
        self.settings_window = None
        self.show()

    def apply_config(self):
        """Применяет настройки конфигурации к интерфейсу."""
        self.username.clear()
        user_list = self.config.get('userSet', {}).get('list', [])
        for user in user_list:
            username = user['username']
            if 'token' in user and user['token']:
                icon = QIcon('assets/microsoft_icon.png')
            else:
                icon = QIcon('assets/pirate_icon.png')
            self.username.addItem(icon, username)
        selected_username = self.config.get('userSet', {}).get('selected', {}).get('username', '')
        if selected_username:
            index = self.username.findText(selected_username)
            if index != -1:
                self.username.setCurrentIndex(index)

    def set_logo_icon(self, path):
        """Устанавливает логотип лаунчера."""
        if os.path.exists(path):
            pixmap = QPixmap(path)
            self.logo.setPixmap(pixmap.scaledToHeight(140)) 
        else:
            logging.warning(f"Logo file not found: {path}")
            QMessageBox.warning(self, "Error", f"Logo file not found: {path}")

    def validate_input(self):
        """Проверяет корректность ввода имени пользователя."""
        if not self.username.currentText().strip():
            QMessageBox.warning(self, "Input Error", "Username не может быть пустым")
            return False
        return True
    
    def check_updates(self):
        """Проверяет наличие обновлений для игры."""
        with open(version, 'r') as f:
            current_version = json.load(f)
        return checkUpdateModpack(current_version['version'])

    def state_update(self, value):
        """Обновляет состояние интерфейса при изменении состояния потока."""
        self.start_button_vanilla.setDisabled(value)
        self.start_progress.setVisible(value)

    def update_progress(self, progress, max_progress, label):
        """Обновляет прогресс-бар."""
        self.start_progress.setValue(progress)
        self.start_progress.setMaximum(max_progress)
        self.start_progress.setFormat(label)

    def launch_game(self):
        """Запускает игру с проверкой обновлений."""
        if not self.validate_input():
            return
        
        self.updateInfo = self.check_updates()

        if self.updateInfo:
            if self.updateInfo.get('updateNeeded', True):
                self.start_button_vanilla.setText('Обновить')
                if downloadUpdateModpack(minecraft_directory, self.updateInfo.get('updateFolder', [])):
                    QMessageBox.information(self, "Обновление", "Идёт скачивание обновления!")
                    self.start_button_vanilla.setText('Играть')
                else:
                    QMessageBox.warning(self, "Ошибка", "Произошла ошибка, попробуйте позже или обратитесь к администратору!")
                    return
            else:
                self.start_button_vanilla.setText('Играть')
        else:
            QMessageBox.warning(self, "Ошибка", "Произошла ошибка, попробуйте позже или обратитесь к администратору!")
            return 
        selected_version = '1.20.4'
        self.launch_thread.launch_setup_signal.emit(selected_version, self.username.currentText(), self.config_options.get('minecraft_folder'))
        self.launch_thread.start()

    def show_error_message(self, title, message):
        """Отображает сообщение об ошибке."""
        QMessageBox.critical(self, title, message)

    def show_folder_minecraft(self):
        """Открывает папку с игрой в файловом менеджере."""
        folder = self.config_options['minecraft_folder']
        if not os.path.exists(folder):
            QMessageBox.warning(self, "Ошибка", "Указанная папка не существует")
            return
        
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            os.system(f"open {folder}")
        else:
            os.system(f"xdg-open {folder}")