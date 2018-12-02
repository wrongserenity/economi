import sys
import pdb

import g
import g_st_menu
import g_enter_name
import g_choose_country
import g_main_menu

import os
import json
from classes import Connection
import logging
from PyQt5 import QtCore, QtGui, QtWidgets

player_start_data = {}


class StandartMenu(QtWidgets.QMainWindow, g_st_menu.Ui_StandartMenu):
    def __init__(self, parent=None):
        super(StandartMenu, self).__init__(parent)
        self.setupUi(self)

        self.label_61.mousePressEvent = self.close_cl
        self.label_63.mousePressEvent = self.menu_close

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def menu_close(self, event):
        self.close()



class Gui(QtWidgets.QMainWindow, g.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setupUi(self)

        self.st_menu = StandartMenu()

        self.label_20.mousePressEvent = self.menu_open

    def menu_open(self, event):
        self.st_menu.showFullScreen()


class EnterName(QtWidgets.QMainWindow, g_enter_name.Ui_EnterName):
    def __init__(self, parent=None):
        super(EnterName, self).__init__(parent)
        self.setupUi(self)

        global player_start_data
        self.dict_ = player_start_data

        self.gui = Gui()

        self.label_7.mousePressEvent = self.close_cl

    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.text_name()

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def text_name(self):
        if self.lineEdit.text():
            self.dict_.update({'name': self.lineEdit.text()})
            self.gui.showFullScreen()
            self.close()
            # тут надо передать даныые из словаря серверу


class EnterCountry(QtWidgets.QMainWindow, g_choose_country.Ui_EnterCountry):
    def __init__(self, parent=None):
        super(EnterCountry, self).__init__(parent)
        self.setupUi(self)

        global player_start_data
        self.dict_ = player_start_data

        self.label_7.mousePressEvent = self.close_cl
        self.label_2.mousePressEvent = self.ch_russia
        self.label_3.mousePressEvent = self.ch_sweden
        self.label_4.mousePressEvent = self.ch_china
        self.label_5.mousePressEvent = self.ch_germany
        self.label_6.mousePressEvent = self.ch_usa

        self.name_enter = EnterName()

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def ch_russia(self, event):
        self.open_game()
        self.dict_.update({'country': 'Russia'})

    def ch_sweden(self, event):
        self.open_game()
        self.dict_.update({'country': 'Sweden'})

    def ch_china(self, event):
        self.open_game()
        self.dict_.update({'country': 'China'})

    def ch_germany(self, event):
        self.open_game()
        self.dict_.update({'country': 'Germany'})

    def ch_usa(self, event):
        self.open_game()
        self.dict_.update({'country': 'USA'})

    def open_game(self):
        self.name_enter.showFullScreen()
        self.close()


class MainMenu(QtWidgets.QMainWindow, g_main_menu.Ui_MainMenu):
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.setupUi(self)

        self.label.mousePressEvent = self.clicked_start
        self.label_7.mousePressEvent = self.close_cl

        self.ch_country = EnterCountry()

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def get_user_id(self):
        try:
            with open("data.json", "r") as file:
                data = file.read()
                data_decoded =  json.loads(data)
                return data_decoded.get('id')
        except Exception as e:
            logging.critical(f"Error occured while trying to read file:\nError: \"{e}\"")
            return False

    def clicked_start(self, event):
        global player_start_data
        self.ch_country.showFullScreen()
        self.close()
        if not os.path.exists("data.json"):
            with open("data.json", "w") as file:
                conn = Connection()
                self._id = conn.get_uid()
                file.write(json.dumps({"id": self._id}))
            player_start_data = {'id': self._id}

        else:
            self._id = self.get_user_id()
            # здесь надо открывать уже сразу окно игры и в брать данные с сервака (имя и странуб и т.д)


def main():
    app = QtWidgets.QApplication(sys.argv)
    menu = MainMenu()
    menu.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
