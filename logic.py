import sys
from g import *
from g_st_menu import *
from PyQt5 import QtCore, QtGui, QtWidgets


class MainWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = MainWindow()
        self.ui.setupUi(self)

        self.menu_opened = False

        self.ui.label_4.mousePressEvent = self.clicked_label_4
        self.ui.label_20.mousePressEvent = self.clicked_menu

    def clicked_label_4(self, event):
        self.ui.label_4.setText('')

    def clicked_menu(self, event):
        if self.menu_opened:
            self.ui.label_20.setText('Suka')
        else:
            app_menu_st = QtWidgets.QApplication(['g_st_menu.py'])
            myapp_menu_st = MenuSt()
            myapp_menu_st.showFullScreen()
            sys.exit(app.exec_())
            sys.exit(app_menu_st.exec_())


class MenuSt(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = MenuStandart()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(['g.py'])
    myapp = MainWin()
    myapp.showFullScreen()
    sys.exit(app.exec_())
