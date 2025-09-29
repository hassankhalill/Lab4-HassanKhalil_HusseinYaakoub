
from PyQt5.QtWidgets import QApplication
from .windows import MainWindow
import sys

def run() -> int:
    """Entry point to launch the PyQt application.

    Returns:
        int: Process exit code.
    """
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()

if __name__ == "__main__":
    raise SystemExit(run())
