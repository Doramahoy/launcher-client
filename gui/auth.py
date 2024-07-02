from PyQt5.QtWidgets import QListWidgetItem, QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QListWidget, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from uuid import uuid1
import os
import logging

try:
    import minecraft_launcher_lib
except ImportError as e:
    logging.error(f"Missing required module: {e}. Please ensure minecraft_launcher_lib is installed.")
    exit(1)

from config.config import load_config, save_config

CLIENT_ID = "a85a2f79-1a21-4869-bb74-1132a755453b"
REDIRECT_URL = "https://login.live.com/oauth20_desktop.srf"

class Auth(QDialog):
    closed = pyqtSignal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        self.init_ui()
        self.config = load_config()
        self.load_user_list()

    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        self.setWindowTitle("Авторизация")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'launcher_icon.ico')))
        self.setFixedSize(800, 500)
        self.setWindowModality(Qt.ApplicationModal)

        self.setStyleSheet("""
            QDialog {
                background-image: url('assets/background_auth.png');
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

        self.web_view = QWebEngineView(self)
        self.web_view.setGeometry(20, 120, 550, 350)
        self.web_view.hide()

        self.username_label = QLabel("Логин:", self)
        self.username_label.setGeometry(170, 120, 250, 50)
        self.username_label.setStyleSheet("color: white; font-size: 20px")

        self.username_input = QLineEdit(self)
        self.username_input.setGeometry(170, 170, 250, 40)
        self.username_input.setMaxLength(16)
        self.username_input.setStyleSheet("font-size: 20px; background-color: rgba(0, 0, 0, 128); border: 1px solid #2C3E50; border-radius: 5px; padding: 5px; color: white;")

        self.auth_type_label = QLabel("Тип аутентификации:", self)
        self.auth_type_label.setStyleSheet("color: white; font-size: 20px")
        self.auth_type_label.setGeometry(170, 20, 250, 50)

        self.auth_type_combo = QComboBox(self)
        self.auth_type_combo.addItems(["Без авторизации", "Microsoft"])
        self.auth_type_combo.setStyleSheet("""
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
        self.auth_type_combo.setGeometry(170, 70, 250, 40)
        self.auth_type_combo.currentIndexChanged.connect(self.update_auth_type)

        self.user_list = QListWidget(self)
        self.user_list.setGeometry(580, 20, 200, 450)
        self.user_list.setStyleSheet("font-size: 20px; background-color: rgba(0, 0, 0, 128); border: 1px solid #2C3E50; border-radius: 5px; padding: 5px; color: white;")
        self.user_list.doubleClicked.connect(self.remove_selected_user)

        self.login_button = QPushButton("Добавить", self)
        self.login_button.setGeometry(170, 220, 250, 50)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 128);
                border-radius: 10px;
                font-size: 30px;
                text-align: center;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 60, 128);
                border-radius: 10px;
                font-size: 32px;
                text-align: center;
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 180, 128);
                border-radius: 10px;
                font-size: 30px;
                text-align: center;
                color: white;
            }
        """)
        self.login_button.clicked.connect(self.login)

    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна."""
        self.closed.emit()
        super().closeEvent(event)

    def update_auth_type(self):
        """Обновляет тип аутентификации."""
        auth_type = self.auth_type_combo.currentText()
        if auth_type == "Microsoft":
            self.username_label.hide()
            self.username_input.hide()
            self.microsoft_login()
            self.login_button.hide()
        else:
            self.login_button.show()
            self.web_view.hide()
            self.username_input.show()
            self.username_label.show()

    def login(self):
        """Обрабатывает нажатие кнопки 'Добавить'."""
        username = self.username_input.text()
        auth_type = self.auth_type_combo.currentText()

        if auth_type == "Без авторизации":
            self.no_account_login(username)
        elif auth_type == "Microsoft":
            self.microsoft_login()

    def no_account_login(self, username):
        """Выполняет вход без аутентификации."""
        if not username:
            QMessageBox.warning(self, "Input Error", "Username не может быть пустым")
            return
        selected_username = self.username_input.text()

        if 'userSet' not in self.config:
            self.config['userSet'] = {
                'selected': {'username': selected_username},
                'list': []
            }
        else:
            self.config['userSet']['selected'] = {'username': selected_username}

        user_list = self.config['userSet'].get('list', [])

        if not any(user['username'] == selected_username for user in user_list):
            user_list.append({'username': selected_username, 'uuid': str(uuid1()), 'token': ''})

        self.config['userSet']['list'] = user_list
        save_config(self.config)
        self.load_user_list()

    def check_token_exists(self):
        """Проверяет наличие токена для текущего пользователя в self.config."""
        user_list = self.config.get('userSet', {}).get('list', [])
        for user in user_list:
            if 'token' in user and user['token']:
                return True
        return False

    def microsoft_login(self):
        """Выполняет вход через Microsoft."""
        self.web_view.show()

        token_exists = self.check_token_exists()

        if token_exists and token_exists != '':
            try:
                minecraft_launcher_lib.microsoft_account.complete_refresh(CLIENT_ID, None, REDIRECT_URL, token_exists)
            except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
                pass

        login_url, self.state, self.code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URL)
        self.web_view.load(QUrl(login_url))

        self.web_view.urlChanged.connect(self.new_url)
        self.web_view.show()

    def new_url(self, url: QUrl):
        """Обрабатывает изменение URL в веб-просмотре."""
        try:
            auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(url.toString(), self.state)
            account_information = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, None, REDIRECT_URL, auth_code, self.code_verifier)
            self.save_account_information(account_information)
            self.web_view.hide()
        except AssertionError:
            print("States do not match!")
        except KeyError:
            print("Url not valid")

    def save_account_information(self, account_information):
        """Сохраняет информацию об учетной записи Microsoft."""
        user_list = self.config['userSet'].get('list', [])
        user_exists = False

        for user in user_list:
            if user['username'] == account_information["name"]:
                user['token'] = account_information['access_token']
                user_exists = True
                break

        if not user_exists:
            user_list.append({'username': account_information["name"], 'uuid': account_information["id"], 'token': account_information['access_token']})

        self.config['userSet']['list'] = user_list
        save_config(self.config)
        self.load_user_list()

    def load_user_list(self):
        """Загружает список пользователей в виджет."""
        self.user_list.clear()
        user_list = self.config.get('userSet', {}).get('list', [])
        for user in user_list:
            item = QListWidgetItem(user['username'])
            if 'token' in user and user['token']:
                item.setIcon(QIcon('assets/microsoft_icon.png'))
            else:
                item.setIcon(QIcon('assets/pirate_icon.png'))
            self.user_list.addItem(item)

    def remove_selected_user(self):
        """Удаляет выбранного пользователя из списка."""
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Пожалуйста, выберите пользователя для удаления")
            return
        selected_item = selected_items[0]
        selected_username = selected_item.text()

        user_list = self.config.get('userSet', {}).get('list', [])
        updated_user_list = [user for user in user_list if user['username'] != selected_username]
        self.config['userSet']['list'] = updated_user_list

        save_config(self.config)
        self.load_user_list()