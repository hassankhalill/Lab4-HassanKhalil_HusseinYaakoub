
from PyQt5.QtWidgets import QMainWindow, QLabel

class MainWindow(QMainWindow):
    """Main application window.

    :ivar label: Central label used for messages.
    :vartype label: PyQt5.QtWidgets.QLabel
    """
    def __init__(self):
        """Initialize the main window and central label."""
        super().__init__()
        self.setWindowTitle("Lab 2 – PyQt App")
        self.label = QLabel("Hello from PyQt!", self)
        self.setCentralWidget(self.label)

    def set_message(self, text: str) -> None:
        """Update the label text.

        :param text: Message to display.
        :type text: str
        """
        self.label.setText(text)
