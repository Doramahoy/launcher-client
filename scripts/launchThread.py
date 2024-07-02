import logging
import subprocess
import os
from PyQt5.QtCore import QThread, pyqtSignal
from config.config import load_config_options, save_config, load_config
from minecraft_launcher_lib.command import get_minecraft_command
from scripts.serverLauncher import download_folder

# Путь к основной директории Minecraft
minecraft_directory = os.path.join(os.path.dirname(__file__), '..', '..')

class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str, str)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)
    game_launched_signal = pyqtSignal()
    game_closed_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.version_id = ''
        self.username = ''
        self.minecraft_folder = ''
        self.progress = 0
        self.progress_max = 0 
        self.progress_label = ''
        self.launch_setup_signal.connect(self.launch_setup)

    def launch_setup(self, version_id, username, minecraft_folder):
        """Настраивает параметры запуска игры."""
        self.version_id = version_id
        self.username = username
        self.minecraft_folder = minecraft_folder

    def update_progress_label(self, value):
        """Обновляет текст метки прогресса."""
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def update_progress(self, value):
        """Обновляет текущее значение прогресса."""
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def update_progress_max(self, value):
        """Обновляет максимальное значение прогресса."""
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_config(self):
        """Обновляет конфигурацию пользователя в конфигурационном файле."""
        self.config = load_config()
        selected_username = self.username

        if 'userSet' not in self.config:
            self.config['userSet'] = {
                'selected': {'username': selected_username},
                'list': []
            }
        else:
            self.config['userSet']['selected'] = {'username': selected_username}
        save_config(self.config)

    def get_user_data(self, username):
        """Возвращает данные пользователя из конфигурационного файла."""
        config = load_config()
        user_list = config.get('userSet', {}).get('list', [])
        for user in user_list:
            if user.get('username') == username:
                return user
        return None

    def run(self):
        """Основной метод, выполняющий запуск Minecraft."""
        self.state_update_signal.emit(True)
        logging.info(f'Starting Minecraft: version={self.version_id}')
        self.update_progress_label("Начало запуска...")
        self.update_config()

        file_patch = os.path.join(minecraft_directory, 'game')

        if not os.path.exists(file_patch):
            self.update_progress_label("Скачивание сборки...")
            try:
                download_folder(self.minecraft_folder)
            except Exception as e:
                logging.error(f'Ошибка при скачивании или распаковке сборки: {e}')
                self.state_update_signal.emit(False)
                return
        
        self.update_progress_label("Подготовка файлов...")
            
        java_path = os.path.join(minecraft_directory, 'jdk-21.0.2', 'bin', 'java.exe')
        self.config_options = load_config_options()
        user_data = self.get_user_data(self.username)

        options = {
            'username': self.username,
            'uuid': user_data['uuid'],
            'token': user_data['token'],
            'executablePath': java_path,
            'jvmArguments': [f"-Xmx{str(self.config_options['allocated_memory'])}G", f"-Xms{str(self.config_options['allocated_memory'])}G"]
        }

        minecraft_command = get_minecraft_command(version=self.version_id, minecraft_directory=file_patch, options=options)
        logging.debug(f"Generated Minecraft command: {' '.join(minecraft_command)}")

        self.update_progress_label("Генерация команды...")

        try:
            # Создание .bat файла для запуска Minecraft
            command_file = os.path.join(file_patch, 'launch_minecraft.bat')
            with open(command_file, 'w') as file:
                fixed_command = []
                for part in minecraft_command:
                    if ' ' in part:
                        fixed_command.append(f'"{part}"')
                    else:
                        fixed_command.append(part)
                file.write(' '.join(fixed_command))
        
            logging.info('Launching Minecraft')
            self.update_progress_label("Запуск игры...")
            self.game_launched_signal.emit()

            process = subprocess.Popen(command_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = process.communicate()
            self.game_closed_signal.emit()
            if process.returncode != 0:
                logging.error(f'Minecraft launch failed with return code {process.returncode}')
                logging.error(f'Stdout: {stdout.decode("utf-8", errors="replace")}')
                logging.error(f'Stderr: {stderr.decode("utf-8", errors="replace")}')
            else:
                logging.info('Minecraft launched successfully')
        except Exception as e:
            logging.error(f'Error launching Minecraft: {e}')

        self.state_update_signal.emit(False)