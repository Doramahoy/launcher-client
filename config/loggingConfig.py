import logging
import coloredlogs

def configure_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        'debug': {'color': 'green'},
        'info': {'color': 'blue'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red', 'bold': True},
        'critical': {'color': 'red', 'bold': True, 'background': 'white'}
    }
    coloredlogs.DEFAULT_FIELD_STYLES = {
        'asctime': {'color': 'magenta'},
        'levelname': {'color': 'cyan', 'bold': True}
    }
    coloredlogs.install(level='DEBUG', fmt=log_format)
    
    file_handler = logging.FileHandler('launcher.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(file_handler)