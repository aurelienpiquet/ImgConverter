import os
from PySide2 import QtWidgets, QtCore, QtGui
from customUi.main_fenetre import MainWindow





if __name__ == '__main__':
    app = QtWidgets.QApplication([])      
    window = MainWindow(ctx=app)
    window.resize(1920 / 4, 1200 / 2)
    window.show()
    app.exec_()