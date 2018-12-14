import sys
import g
import g_st_menu
import g_enter_name
import g_choose_country
import g_main_menu
import g_player_menu
import background
import g_pl_menu_plus_st_menu
import tornado.tcpclient
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
window_opened = 'market'
player_opened = None


ready_ = False


def update():
    pass


class Connection(object):
    client = tornado.tcpclient.TCPClient()
    loop = asyncio.get_event_loop()

    def __init__(self, ip="193.187.172.195", port="8080"):
        self.HOST = ip
        self.PORT = port

    @staticmethod
    def format_(obj, out=False):
        return bytes(f"{json.dumps(obj)}\n", "utf-8") if out else json.loads(obj.decode("utf-8"))

    async def __send_request(self, msg):
        client = tornado.tcpclient.TCPClient()
        stream = await client.connect("193.187.172.195", "8080")
        # stream.write(bytes("fuck you\n", "utf-8"))
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
    # переход по страницам в Market, Exchange и Units
    def scroll_up(self, event):
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
        global window_opened
        if  window_opened != 'market':
            conn = Connection()
            market_units = conn.get_market_units()
            self.price_1.setText(str(market_units[0]['price']))
            self.prod_1.setText(str(market_units[0]['prod']))
            self.steps_1.setText(str(market_units[0]['steps']))
            self.level_1.setText(str(market_units[0]['level']))

            self.price_2.setText(str(market_units[1]['price']))
            self.prod_2.setText(str(market_units[1]['prod']))
            self.steps_2.setText(str(market_units[1]['steps']))
            self.level_2.setText(str(market_units[1]['level']))

            self.price_3.setText(str(market_units[2]['price']))
            self.prod_3.setText(str(market_units[2]['prod']))
            self.steps_3.setText(str(market_units[2]['steps']))
            self.level_3.setText(str(market_units[2]['level']))

            self.price_4.setText(str(market_units[3]['price']))
            self.prod_4.setText(str(market_units[3]['prod']))
            self.steps_4.setText(str(market_units[3]['steps']))
            self.level_4.setText(str(market_units[3]['level']))

            window_opened = 'market'

    # аналогичная функция для изменения переменных, выводимых на экран
    # только тут должны "хранится" данные о юнитах, выставленных на
    # продажу другими игроками
    def exchange_open(self, event):
        global window_opened
        if window_opened != 'exchange':
            conn = Connection()
            exchange_units = conn.get_exchange_units()
            self.price_1.setText(str(exchange_units[0]['price']))
            self.prod_1.setText(str(exchange_units[0]['prod']))
            self.steps_1.setText(str(exchange_units[0]['steps']))
            self.level_1.setText(str(exchange_units[0]['level']))

            self.price_2.setText(str(exchange_units[1]['price']))
            self.prod_2.setText(str(exchange_units[1]['prod']))
            self.steps_2.setText(str(exchange_units[1]['steps']))
            self.level_2.setText(str(exchange_units[1]['level']))

            self.price_3.setText(str(exchange_units[2]['price']))
            self.prod_3.setText(str(exchange_units[2]['prod']))
            self.steps_3.setText(str(exchange_units[2]['steps']))
            self.level_3.setText(str(exchange_units[2]['level']))

            self.price_4.setText(str(exchange_units[3]['price']))
            self.prod_4.setText(str(exchange_units[3]['prod']))
            self.steps_4.setText(str(exchange_units[3]['steps']))
            self.level_4.setText(str(exchange_units[3]['level']))

            window_opened = 'exchange'

    # опять же похожа функция, но выводит доступные игроку юниты
    def units_open(self, event):
        global window_opened
        if window_opened != 'units':
            conn = Connection()
            units_units = conn.get_player_units()
            self.price_1.setText(str(units_units[0]['price']))
            self.prod_1.setText(str(units_units[0]['prod']))
            self.steps_1.setText(str(units_units[0]['steps']))
            self.level_1.setText(str(units_units[0]['level']))

            self.price_2.setText(str(units_units[1]['price']))
            self.prod_2.setText(str(units_units[1]['prod']))
            self.steps_2.setText(str(units_units[1]['steps']))
            self.level_2.setText(str(units_units[1]['level']))

            self.price_3.setText(str(units_units[2]['price']))
            self.prod_3.setText(str(units_units[2]['prod']))
            self.steps_3.setText(str(units_units[2]['steps']))
            self.level_3.setText(str(units_units[2]['level']))

            self.price_4.setText(str(units_units[3]['price']))
            self.prod_4.setText(str(units_units[3]['prod']))
            self.steps_4.setText(str(units_units[3]['steps']))
            self.level_4.setText(str(units_units[3]['level']))

            window_opened = 'units'

    # продажа или покупка юнитов
    # или поднять уровень юнита / продать
    # о - некоторое положительное действие - покупка, поднять level
    # x - некоторое отрицательное дейстивие - продажа
    # x активна только в окне Units
    # должны срабатывать, только когда global ready_ - False
    def o1(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'market':
            conn.buy_m(0)
        elif window_opened == 'units':
            conn.lvl_up(0)
        elif window_opened == 'exchange':
            conn.buy_ex(0)

    def x1(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'units':
            conn.sell_un(0)

    def o2(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'market':
            conn.buy_m(1)
        elif window_opened == 'units':
            conn.lvl_up(1)
        elif window_opened == 'exchange':
            conn.buy_ex(1)

    def x2(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'units':
            conn.sell_un(0)

    def o3(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'market':
            conn.buy_m(2)
        elif window_opened == 'units':
            conn.lvl_up(2)
        elif window_opened == 'exchange':
            conn.buy_ex(2)

    def x3(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'units':
            conn.sell_un(0)

    def o4(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'market':
            conn.buy_m(3)
        elif window_opened == 'units':
            conn.lvl_up(3)
        elif window_opened == 'exchange':
            conn.buy_ex(3)

    def x4(self, event):
        global window_opened
        conn = Connection()
        if window_opened == 'units':
            conn.sell_un(0)


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
        self.menu.mousePressEvent = self.menu_open
        self.exit.mousePressEvent = self.player_cl

        # market, exchange, units
        self.market.mousePressEvent = self.market_open
        self.exchange.mousePressEvent = self.exchange_open
        self.units.mousePressEvent = self.units_open

        self.o1.mousePressEvent = self.o1
        self.x1.mousePressEvent = self.x1
        self.o2.mousePressEvent = self.o2
        self.x2.mousePressEvent = self.x2
        self.o3.mousePressEvent = self.o3
        self.x3.mousePressEvent = self.x3
        self.o4.mousePressEvent = self.o4
        self.x4.mousePressEvent = self.x4

        self.next.mousePressEvent = self.next_move

        self.buy.mousePressEvent = self.buy_value

        global ready_
        if ready_:
            self.next.setText('wait')

    def buy_value(self, event):
        global player_opened
        conn = Connection()
        if self.value_buy.text():
            try:
                conn.buy_value(int(self.value_buy.text()), player_opened)
            except Exception:
                pass

    def next_move(self, event):
        global ready_
        ready_ = True
        self.next.setText('wait')

    def menu_open(self, event):
        self.pl_and_sr_menu = PlayerAndStandartMenu()
        self.pl_and_sr_menu.showFullScreen()
        self.close()

    def player_cl(self, event):
        global player_opened
        player_opened = None
        self.gui = Gui()
        self.gui.showFullScreen()
        self.close()


# окно с меню игрока и обычным меню, которое открывается слева снизу
class PlayerAndStandartMenu(QtWidgets.QMainWindow, g_pl_menu_plus_st_menu.Ui_PlMenuSt, MarketExchangeUnits):
    def __init__(self, parent=None):
        super(PlayerAndStandartMenu, self).__init__(parent)
        self.setupUi(self)

        self.exit.mousePressEvent = self.close_cl
        self.menu.mousePressEvent = self.menu_hide

        self.player_open.mousePressEvent = self.player_cl

        # market, echange, units
        self.market.mousePressEvent = self.market_open
        self.exchange.mousePressEvent = self.exchange_open
        self.units.mousePressEvent = self.units_open

        self.o1.mousePressEvent = self.o1
        self.x1.mousePressEvent = self.x1
        self.o2.mousePressEvent = self.o2
        self.x2.mousePressEvent = self.x2
        self.o3.mousePressEvent = self.o3
        self.x3.mousePressEvent = self.x3
        self.o4.mousePressEvent = self.o4
        self.x4.mousePressEvent = self.x4

        self.next.mousePressEvent = self.next_move

        self.buy.mousePressEvent = self.buy_value

        global ready_
        if ready_:
            self.next.setText('wait')

    def buy_value(self, event):
        global player_opened
        conn = Connection()
        if self.value_buy.text():
            try:
                conn.buy_value(int(self.value_buy.text()), player_opened)
            except Exception:
                pass

    def next_move(self, event):
        global ready_
        ready_ = True
        self.next.setText('wait')

    def player_cl(self, event):
        global player_opened
        player_opened = None
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

        self.exit.mousePressEvent = self.close_cl
        self.hide.mousePressEvent = self.menu_hide
        self.player_1.mousePressEvent = self.player_one
        self.player_2.mousePressEvent = self.player_two
        self.player_3.mousePressEvent = self.player_three

        # market, echange, units
        self.market.mousePressEvent = self.market_open
        self.exchange.mousePressEvent = self.exchange_open
        self.units.mousePressEvent = self.units_open

        self.o1.mousePressEvent = self.o1
        self.x1.mousePressEvent = self.x1
        self.o2.mousePressEvent = self.o2
        self.x2.mousePressEvent = self.x2
        self.o3.mousePressEvent = self.o3
        self.x3.mousePressEvent = self.x3
        self.o4.mousePressEvent = self.o4
        self.x4.mousePressEvent = self.x4

        self.next.mousePressEvent = self.next_move

        global ready_
        if ready_:
            self.next.setText('wait')

    def next_move(self, event):
        global ready_
        ready_ = True
        self.next.setText('wait')

    def player_one(self, event):
        global player_opened
        player_opened = None
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
class Gui(QtWidgets.QMainWindow, g.Ui_MainGUI, MarketExchangeUnits):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setupUi(self)

        # menu
        self.menu.mousePressEvent = self.menu_open

        # players
        self.player_1.mousePressEvent = self.player_one
        self.player_2.mousePressEvent = self.player_two
        self.player_3.mousePressEvent = self.player_three

        # market, echange, units
        self.market.mousePressEvent = self.market_open
        self.exchange.mousePressEvent = self.exchange_open
        self.units.mousePressEvent = self.units_open

        self.o1.mousePressEvent = self.o1
        self.x1.mousePressEvent = self.x1
        self.o2.mousePressEvent = self.o2
        self.x2.mousePressEvent = self.x2
        self.o3.mousePressEvent = self.o3
        self.x3.mousePressEvent = self.x3
        self.o4.mousePressEvent = self.o4
        self.x4.mousePressEvent = self.x4

        self.up.mousePressEvent = self.scroll_up
        self.down.mousePressEvent = self.scroll_down

        self.next.mousePressEvent = self.next_move
        self.player_value.setText('oop')

        global ready_
        if ready_:
            self.next.setText('wait')

    def next_move(self, event):
        global ready_
        ready_ = True
        self.next.setText('wait')

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

    # todo: после введения данных и отправки на сервак надо бы отправлять id другим игрокам, которые зайдут позже
    # так же надо получать инофрмацию об id игроков5
    def text_name(self):
        if self.lineEdit.text():
            import pdb
            pdb.set_trace()
            self.gui = Gui()
            self.dict_.update({'name': self.lineEdit.text()})

            conn = Connection()
            uid = conn.set_user_data(self.dict_)
            self.dict_.update({'id': uid})
            with open("data.json", "w") as file:
                file.write(str(self.dict_['id']))

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
                return data_decoded
        except Exception as e:
            logging.critical(f"Error occured while trying to read file:\nError: \"{e}\"")
            return False

    def clicked_start(self, event):
        global player_start_data
        self.ch_country.showFullScreen()
        self.close()
        if os.path.exists("data.json"):
            import pdb
            pdb.set_trace()
            self._id = self.get_user_id()
            global players_data
            players_data.append(self._id)
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