
from PyQt5.QtWidgets import QPushButton

class HelloButton(QPushButton):
    """A simple custom button widget.

    :param text: The text displayed on the button.
    :type text: str
    """
    def __init__(self, text: str = "Click Me!"):
        """Initialize the HelloButton."""
        super().__init__(text)

    def say_hello(self) -> str:
        """Return a friendly greeting.

        :return: Greeting string
        :rtype: str
        """
        return "Hello from PyQt!"
