from pathlib import Path
import os
import sys

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine

if __name__ == "__main__":

    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_icon_path = os.path.join(current_dir, 'icons', 'brain.png')
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(app_icon_path))
    engine = QQmlApplicationEngine()

    # Load application controller and handle configuration errors
    try:
        from controllers import applicationcontroller
        appController = applicationcontroller.ApplicationController()
    except Exception as e:
        QMessageBox.critical(None, "Error", str(e))
        sys.exit(-1)
    engine.rootContext().setContextProperty("appController", appController)
    qml_file = Path(__file__).resolve().parent / "Main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
