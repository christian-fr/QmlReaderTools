__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "1.0.4"
__status__ = "Prototype"
__name__ = "QmlReader_GUI"
# last edited 2020-04-01

import MainInterface
from tkinter import Tk

root = Tk()
app = MainInterface.Window(root)
root.wm_title("QML Reader " + str(__version__))
root.geometry('800x600')
root.mainloop()
