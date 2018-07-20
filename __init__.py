import MainWindow
import os
import sys
try:
    def __init__(self):
        self.menuBar.addmenuitem('Plugin', 'command', 'ValidatorDB', label='ValidatorDB',
                                 command=lambda s=self: MainWindow.MainWindow())

        path = os.path.dirname(__file__)
        sys.path.append(path)
except (ImportError, NameError):
    pass