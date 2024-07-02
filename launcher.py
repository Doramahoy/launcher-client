import sys
from PyQt5.QtWidgets import QApplication
from config.loggingConfig import configure_logging
from gui.mainWindow import MainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtCore import QLocale

if __name__ == '__main__':
    configure_logging()
    app = QApplication(sys.argv)
    QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name().split("_")[0])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())