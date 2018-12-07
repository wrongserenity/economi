import sys
import g
import g_st_menu
import g_enter_name
import g_choose_country
import g_main_menu
import g_player_menu
import background
import g_pl_menu_plus_st_menu
import tornado
import asyncio
import os
import json
import logging
from PyQt5 import QtCore, QtGui, QtWidgets


# тут хранятся данные об игрока, отправляемы на сервер, когда
# игрок вводит свое имя
# сервер отправляет в ответ id и все данные связанные с выбранной
# страной и сохраняет в полях класса игрока
player_start_data = {}
players_data = []
ready_ = False


def update():
    pass


class Connection(object):
    client = tornado.tcpclient.TCPClient()
    loop = asyncio.get_event_loop()

    def __init__(self, ip="0.0.0.0", port="8008"):
        self.HOST = ip
        self.PORT = port

    @staticmethod
    def format_(obj, out=False):
        return bytes(f"{json.dumps(obj)}\n", "utf-8") if out else json.loads(obj.decode("utf-8"))

    async def __send_request(self, msg):
        stream = await self.client.connect(self.HOST, self.PORT)
        stream.write(self.format_(msg, out=True))
        response = await stream.read_until(b"\n")
        return self.format_(response)

    def get_units(self, uid):
        return self.__request({"action": "get_units", "args": {"uid": uid}})

    def get_unit(self, unit_id):
        return self.__request({"action": "get_unit", "args": {"unit_id": unit_id}})

    def get_user_data(self, uid):
        return self.__request({"action": "get_user_data", "args": {"uid": uid}})

    def get_market_units(self):
        return self.__request({"action":"get_market_units", "args": {}})

    def set_user_data(self, user_dict):
        return self.__request({"action": "set_user_data", "args": {"user_dict": user_dict}})

    def update_user_data(self, user_dict):
        return self.__request({"action": "update_user_data", "args": {"user_dict": user_dict}})

    def remove_unit(self, owner_id, unit_id):
        return self.__request({"action": "remove_unit", "args": {"unit_id": unit_id}})

    def new_unit(self, unit_dict):
        return self.__request({"action": "new_unit", "args": {"unit_dict": unit_dict}})

    def update_unit(self, unit_id, new_dict):
        return self.__request({"action": "update_unit", "args": {"unit_id": unit_id, "unit_dict": new_dict}})

    def get_uid(self):
        return self.__request({"action": "get_uid"})

    def __request(self, req):
        return self.loop.run_until_complete(self.__send_request(req))



# отвечает за нажатие на кнопку "buy" в поле покупки валюты
class PlayerValueBuy:
    def buy_press(self, event):
        pass


# отвечает за все операции над окнами Market, Exchange и Units
class MarketExchangeUnits(object):
    gui_window_name = None
    # переменные, в которые надо подгружать информацию с сервака
    # при нажатии на Market / Exchange / Units справа в окне
    # label_86 price1
    # label_87 prod1
    # label_88 steps1
    # label_89 level1

    # label_54 price2
    # label_55 prod2
    # label_56 steps2
    # label_57 level2

    # label_58 price3
    # label_66 prod3
    # label_67 steps3
    # label_68 level3

    # label_44 price4
    # label_47 prod4
    # label_49 steps4
    # label_51 level4

    # переход по страницам в Market, Exchange и Units
    class ScrollUp(object):
        def __init__(self, gui_window_name):
            self.gui_window_name = gui_window_name

        def __call__(self, event):
            pass

    def scroll_down(self, event):
        pass

    # меняеет данные на те, что должен выводить Market: четыре юнита и
    # каждый со своими характеристиками
    # если для вывода не хватает юнита, то делается запрос на сервер для
    # создания объекта класса юнит
    # причем, сервер на полурандоме выставляет значения, билзкие к тем,
    # что написаны в unit.py (в нем прописаны сложности юнита, которые
    # зависят от момента игры, ведь с ростом фонда появится нужда в более
    # производительных юнитах)
    def market_open(self, event):
        conn = Connection()
        self.gui_window_name = "market"
        market_units = conn.get_market_units()
        pass

    # аналогичная функция для изменения переменных, выводимых на экран
    # только тут должны "хранится" данные о юнитах, выставленных на
    # продажу другими игроками
    def exchange_open(self, event):
        self.gui_window_name = "exchange"
        pass

    # опять же похожа функция, но выводит доступные игроку юниты
    def units_open(self, event):
        self.gui_window_name = "units"
        pass

    # продажа или покупка юнитов
    # или поднять уровень юнита / продать
    # о - некоторое положительное действие - покупка, поднять level
    # x - некоторое отрицательное дейстивие - продажа
    # x активна только в окне Units
    # должны срабатывать, только когда global ready_ - False
    def o1(self, event):
        pass

    def x1(self, event):
        pass

    def o2(self, event):
        pass

    def x2(self, event):
        pass

    def o3(self, event):
        pass

    def x3(self, event):
        pass

    def o4(self, event):
        pass

    def x4(self, event):
        pass


# это тупо фон, чтобы при переходах не моргал рабочий стол
class Background(QtWidgets.QMainWindow, background.Ui_BackGround):
    def __init__(self, parent=None):
        super(Background, self).__init__(parent)
        self.setupUi(self)


# окно только с меню игрока (нажатие на игрока слева сверху)
class PlayerMenu(QtWidgets.QMainWindow, g_player_menu.Ui_PlayerMenu, MarketExchangeUnits):
    def __init__(self, parent=None):
        super(PlayerMenu, self).__init__(parent)
        self.setupUi(self)

        # закрытие меню игрока и открытие обычного меню
        self.label_20.mousePressEvent = self.menu_open
        self.label_4.mousePressEvent = self.player_cl

        # market, exchange, units
        self.label.mousePressEvent = self.market_open
        self.label_2.mousePressEvent = self.exchange_open
        self.label_3.mousePressEvent = self.units_open

        self.label_70.mousePressEvent = self.o1
        self.label_74.mousePressEvent = self.x1
        self.label_68.mousePressEvent = self.o2
        self.label_73.mousePressEvent = self.x2
        self.label_61.mousePressEvent = self.o3
        self.label_71.mousePressEvent = self.x3
        self.label_67.mousePressEvent = self.o4
        self.label_72.mousePressEvent = self.x4

        self.label_19.mousePressEvent = self.next_move

        global ready_
        if ready_:
            self.label_19.setText('wait')

    def next_move(self, event):
        global ready_
        ready_ = True
        self.label_19.setText('wait')

    def menu_open(self, event):
        self.pl_and_sr_menu = PlayerAndStandartMenu()
        self.pl_and_sr_menu.showFullScreen()
        self.close()

    def player_cl(self, event):
        self.gui = Gui()
        self.gui.showFullScreen()
        self.close()


# окно с меню игрока и обычным меню, которое открывается слева снизу
class PlayerAndStandartMenu(QtWidgets.QMainWindow, g_pl_menu_plus_st_menu.Ui_PlMenuSt, MarketExchangeUnits):
    def __init__(self, parent=None):
        super(PlayerAndStandartMenu, self).__init__(parent)
        self.setupUi(self)

        self.label_61.mousePressEvent = self.close_cl
        self.label_63.mousePressEvent = self.menu_hide

        self.label_4.mousePressEvent = self.player_cl

        # market, echange, units
        self.label.mousePressEvent = self.market_open
        self.label_2.mousePressEvent = self.exchange_open
        self.label_3.mousePressEvent = self.units_open

        self.label_73.mousePressEvent = self.o1
        self.label_77.mousePressEvent = self.x1
        self.label_72.mousePressEvent = self.o2
        self.label_76.mousePressEvent = self.x2
        self.label_74.mousePressEvent = self.o3
        self.label_78.mousePressEvent = self.x3
        self.label_75.mousePressEvent = self.o4
        self.label_79.mousePressEvent = self.x4

        self.label_19.mousePressEvent = self.next_move

        global ready_
        if ready_:
            self.label_19.setText('wait')

    def next_move(self, event):
        global ready_
        ready_ = True
        self.label_19.setText('wait')

    def player_cl(self, event):
        self.st_menu = StandartMenu()
        self.st_menu.showFullScreen()
        self.close()

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def menu_hide(self, event):
        self.p_menu = PlayerMenu()
        self.p_menu.showFullScreen()
        self.close()


# обыное меню с кнопками exit и hide (скрыть меню)
class StandartMenu(QtWidgets.QMainWindow, g_st_menu.Ui_StandartMenu, MarketExchangeUnits):
    def __init__(self, parent=None):
        super(StandartMenu, self).__init__(parent)
        import pdb
        # pdb.set_trace()
        self.setupUi(self)

        self.label_61.mousePressEvent = self.close_cl
        self.label_63.mousePressEvent = self.menu_hide
        self.label_4.mousePressEvent = self.player_one
        self.label_5.mousePressEvent = self.player_two
        self.label_6.mousePressEvent = self.player_three

        # market, echange, units
        self.label.mousePressEvent = self.market_open
        self.label_2.mousePressEvent = self.exchange_open
        self.label_3.mousePressEvent = self.units_open

        self.label_71.mousePressEvent = self.o1
        self.label_75.mousePressEvent = self.x1
        self.label_70.mousePressEvent = self.o2
        self.label_74.mousePressEvent = self.x2
        self.label_70.mousePressEvent = self.o3
        self.label_74.mousePressEvent = self.x3
        self.label_72.mousePressEvent = self.o4
        self.label_76.mousePressEvent = self.x4

        self.label_19.mousePressEvent = self.next_move

        global ready_
        if ready_:
            self.label_19.setText('wait')

    def next_move(self, event):
        global ready_
        ready_ = True
        self.label_19.setText('wait')

    def player_one(self, event):
        self.player_open()

    def player_two(self, event):
        self.player_open()

    def player_three(self, event):
        self.player_open()

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def menu_hide(self, event):
        self.gui = Gui()
        self.gui.showFullScreen()
        self.close()

    def player_open(self):
        self.pl_and_st_menu = PlayerAndStandartMenu()
        self.pl_and_st_menu.showFullScreen()
        self.close()


# основное окно без открытых меню
class Gui(QtWidgets.QMainWindow, g.Ui_MainWindow, MarketExchangeUnits):
    def __init__(self, parent=None):
        self.st_menu = None
        super(Gui, self).__init__(parent)
        self.setupUi(self)

        # menu
        self.label_20.mousePressEvent = self.menu_open

        # players
        self.label_4.mousePressEvent = self.player_one
        self.label_5.mousePressEvent = self.player_two
        self.label_6.mousePressEvent = self.player_three

        # market, echange, units
        self.label.mousePressEvent = self.market_open
        self.label_2.mousePressEvent = self.exchange_open
        self.label_3.mousePressEvent = self.units_open

        self.label_90.mousePressEvent = self.o1
        self.label_91.mousePressEvent = self.x1
        self.label_62.mousePressEvent = self.o2
        self.label_72.mousePressEvent = self.x2
        self.label_69.mousePressEvent = self.o3
        self.label_74.mousePressEvent = self.x3
        self.label_61.mousePressEvent = self.o4
        self.label_71.mousePressEvent = self.x4

        scroll_up = self.ScrollUp(self.gui_window_name)
        self.label_52.mousePressEvent = scroll_up
        self.label_53.mousePressEvent = self.scroll_down

        self.label_19.mousePressEvent = self.next_move

        global ready_
        if ready_:
            self.label_19.setText('wait')

    def next_move(self, event):
        global ready_
        ready_ = True
        self.label_19.setText('wait')

    def player_one(self, event):
        self.player_open()

    def player_two(self, event):
        self.player_open()

    def player_three(self, event):
        self.player_open()

    # здесь так же надо продумать, как можно сделать так, чтобы при нажатии,
    # например, на player2 выводилась информация именно по второму игроку
    def player_open(self):
        self.player_menu = PlayerMenu()
        self.player_menu.showFullScreen()
        self.close()

    def menu_open(self, event):
        self.st_menu = StandartMenu()
        self.st_menu.showFullScreen()
        self.close()


# окно ввода имени
class EnterName(QtWidgets.QMainWindow, g_enter_name.Ui_EnterName):
    def __init__(self, parent=None):
        super(EnterName, self).__init__(parent)
        self.setupUi(self)

        global player_start_data
        self.dict_ = player_start_data

        self.label_7.mousePressEvent = self.close_cl

    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.text_name()

    def close_cl(self, event):
        QtCore.QCoreApplication.instance().quit()

    def text_name(self):
        if self.lineEdit.text():
            self.gui = Gui()
            self.dict_.update({'name': self.lineEdit.text()})
            conn = Connection()
            uid = conn.set_user_data(self.dict_)
            self.dict_.update({'id': uid})
            with open("data.json", "w") as file:
                file.write(self.dict_['id'])
            self.gui.showFullScreen()
            self.close()
            # тут надо передать даныые из словаря серверу


# окно выбора страны
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

    # здесь надо отправлять данные об имени и стране на сервак
    def open_game(self):
        self.name_enter = EnterName()
        self.name_enter.showFullScreen()
        self.close()


# окно, открывающееся при запуске игры
class MainMenu(QtWidgets.QMainWindow, g_main_menu.Ui_MainMenu):
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.setupUi(self)

        self.label.mousePressEvent = self.clicked_start
        self.label_7.mousePressEvent = self.close_cl

        self.ch_country = EnterCountry()
        self.bg = Background()
        self.bg.showFullScreen()

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
        if os.path.exists("data.json"):
            self._id = self.get_user_id()
            conn = Connection()
            data = conn.get_user_data(self._id)
            player_start_data = dict(id=self._id, **data)
            # здесь надо открывать уже сразу окно игры и в брать данные с сервака (имя и странуб и т.д)


def main():
    app = QtWidgets.QApplication(sys.argv)
    menu = MainMenu()
    menu.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
