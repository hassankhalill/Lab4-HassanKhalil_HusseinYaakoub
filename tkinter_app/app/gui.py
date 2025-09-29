# app/gui.py
import tkinter as tk

class CounterApp:
    """
    A very small Tkinter demo app with a button and a label.

    :param title: Window title to display.
    :type title: str
    """

    def __init__(self, title: str = "Lab 2 – Tkinter Demo"):
        """Constructor method."""
        self.root = tk.Tk()
        self.root.title(title)

        self._count = 0

        self.label = tk.Label(self.root, text="Count: 0")
        self.label.pack(padx=12, pady=8)

        self.button = tk.Button(self.root, text="Increment", command=self.increment)
        self.button.pack(padx=12, pady=8)

    def increment(self):
        """
        Increase the counter and update the label.

        :raises RuntimeError: If internal counter state becomes invalid.
        :return: None
        :rtype: None
        """
        self._count += 1
        if self._count < 0:
            raise RuntimeError("Counter corrupted")
        self.label.config(text=f"Count: {self._count}")

    def run(self):
        """
        Start the Tkinter main loop.

        :return: None
        :rtype: None
        """
        self.root.mainloop()


def main():
    """
    Launch the CounterApp.

    :return: None
    :rtype: None
    """
    app = CounterApp()
    app.run()


if __name__ == "__main__":
    main()
