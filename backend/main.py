"""CLI entry point for launching the application GUIs.

This module provides a small wrapper around :mod:`argparse` to launch either
the PyQt5 or Tkinter frontends. It is safe to import during Sphinx builds as
no GUI is created at import time.
"""

import argparse


def main():
    """Parse CLI arguments and run the selected GUI.

    Use ``--qt`` to run the PyQt5 GUI or ``--tk`` to run the Tkinter GUI
    (default). If both are omitted, Tkinter is used.
    """
    
    prs = argparse.ArgumentParser(description="School Management System launcher")
    prs.add_argument("--qt", action="store_true", help="Run PyQt5 GUI")
    prs.add_argument("--tk", action="store_true", help="Run Tkinter GUI (default)")
    arg = prs.parse_args()

    if arg.qt and not arg.tk:

        from pyqt_app import run
        run()

    else:
        from tkinter_app import run

        run()


if __name__ == "__main__":
    main()