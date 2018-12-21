import tornado
import socket
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.tcpserver
import tornado.tcpclient
import mongo
import postgres
from itertools import count
import json

from postgres import PostgresConnection
from mongo import MongoConnection
from unit import unit_coef, level_coef, pages, min_value_percent
import copy
# from for_server import game, market, exchange

import random

ready_players = []


class EconomiTcpServer(object):
    connection_id = count(0, 1)

    def __init__(self, stream, mongo_conn, postgres_conn):
        super().__init__()
        self.mongo_connection = mongo_conn
        self.postgres_connection = postgres_conn
        self.stream = stream
        self.id = self.connection_id.__next__()
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.stream.set_close_callback(self.on_disconnect)

    def get_units(self, uid):
        return self.mongo_connection.get_units(uid)

    def get_unit(self, unit_id):
        return self.mongo_connection.get_unit(unit_id)

    def get_player_data(self, uid):
        data = self.postgres_connection.get_data(uid)
        return data
        # dict_ = {'id': uid}
        # position = game.players_id.index(uid)
        # args = ['value', 'gdp']
        # for arg in args:
        #   dict_.update({arg: game.player[position].__dict__[arg]})

    def get_user_data(self, uid):
        game.players.append(Player(uid, None, None, None, None))
        game.players_id.append(uid)
        if len(game.players) == 4:
            game.start()
        return game.players[-1].to_dict()

    def set_user_data(self, user_dict):
        res_id = self.postgres_connection.set_data(user_dict)
        game.players.append(Player(res_id, user_dict["name"], user_dict["country"],
                                   *Player.country_st.get(user_dict["country"])))
        if len(game.players) == 4:
            game.start()
        return res_id

    def update_user_data(self, user_dict):
        return self.postgres_connection.update_data(user_dict)

    def new_unit(self, unit_dict):
        return self.mongo_connection.new_unit(unit_dict)

    def update_unit(self, unit_id, unit_dict):
        return self.mongo_connection.update_unit(unit_id, unit_dict)

    def remove_unit(self, unit_id):
        self.mongo_connection.remove_unit(unit_id)

    @staticmethod
    def format_(obj, out=False):
        print(str(obj))
        return bytes(f'{json.dumps(obj)}\n', "utf-8") if out else json.loads(obj.decode("utf-8"))

    @tornado.gen.coroutine
    def on_disconnect(self):
        self.log(f"Connection {self.id} disconnected")
        yield []

    @tornado.gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                data = self.format_(line)
                if data['action'] == "get_units" and "uid" in data['args'].keys():
                    out = self.get_units(data['args']['uid'])
                elif data['action'] == "get_unit" and "unit_id" in data['args'].keys():
                    out = self.get_unit(data['args']['unit_id'])
                elif data['action'] == "remove_unit" and "unit_id" in data['args'].keys():
                    out = self.remove_unit(data['args']['unit_id'])
                elif data['action'] == "get_user_data" and "uid" in data['args'].keys():
                    out = self.get_user_data(data['args']['uid'])
                elif data['action'] == "set_user_data" and "user_dict" in data['args'].keys():
                    value, gdp = Player.country_st[data['args']['user_dict']['country']]
                    data['args']['user_dict'].update({'value': value, "gdb": gdp})
                    out = self.set_user_data(data['args']['user_dict'])

                elif data['action'] == "get_other":
                    data = [player.to_dict() for player in game.players if player.id not in [data['args']['id'],
                                                                                             *data['args']['other']]]
                    out = data
                elif data['action'] == 'update':
                    out = [player.to_dict() for player in game.players]

                elif data['action'] == "update_user_data" and "user_dict" in data['args'].keys():
                    out = self.update_user_data(data['args']['user_dict'])
                elif data['action'] == "new_unit" and "unit_dict" in data['args'].keys():
                    out = self.new_unit(data['args']['unit_dict'])
                elif data['action'] == "update_unit" and "unit_id" in data['args'].keys() \
                        and "unit_dict" in data['args'].keys():
                    out = self.update_unit(data['args']['unit_id'], data['args']['unit_dict'])
                elif data["action"] == "get_uid":
                    out = self.postgres_connection.get_uid()
                elif data["action"] == "get_player_data":
                    out = self.get_player_data(data["args"]["uid"])

                elif data['action'] == 'get_game_data':
                    self.postgres_connection.update_game_data(game.new_rate)
                    out = self.postgres_connection.get_game_data()

                elif data['action'] == 'buy_value':
                    sum_ = data['args']['sum']
                    try:
                        sum_ = int(sum_)
                    except:
                        return False
                    id_ = data['args']['id']
                    uid = data['args']['uid']
                    import pdb
                    pdb.set_trace()
                    # TODO: ЕЩЁ КОСТЫЛЬ
                    game.players[game.players_id.index(int(uid))].buy_value(sum_, int(id_))

                elif data['action'] == 'next_move_ready':
                    uid = data['args']
                    global ready_players
                    if uid not in ready_players:
                        ready_players.append(uid)
                    if len(ready_players) == 4:
                        game.next_move()
                        return 1
                    else:
                        return 0

                else:
                    out = "Error occurred"

                self.log('got |%s|' % str(data))
                yield self.stream.write(self.format_(out if out else "", out=True))
        except tornado.iostream.StreamClosedError:
            pass

    @tornado.gen.coroutine
    def on_connect(self):
        raddr = 'closed'
        try:
            raddr = '%s:%d' % self.stream.socket.getpeername()
        except Exception:
            pass
        self.log('new, %s' % raddr)

        yield self.dispatch_client()

    def log(self, msg, *args, **kwargs):
        print('[Connection %d] %s' % (self.id, msg))


class TcpServer(tornado.tcpserver.TCPServer):
    mongo_connection = mongo.MongoConnection("test-database", 'test-col')
    postgres_connection = postgres.PostgresConnection()

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        """
        Called for each new connection, stream.socket is
        a reference to socket object
        """
        connection = EconomiTcpServer(stream, self.mongo_connection, self.postgres_connection)
        yield connection.on_connect()

    def run_(self):
        # configuration
        host = '193.187.172.195'
        port = 8080

        # tcp server
        self.listen(port, host)
        print("Li-stening on %s:%d..." % (host, port))

        # infinite loop
        tornado.ioloop.IOLoop.instance().start()


class Player(object):
    country_st = {'Russia': [700, 1.09],
                  'USA': [400, 1.2],
                  'Germany': [550, 1.12],
                  'China': [300, 1.25],
                  'Sweden': [500, 1.17]}

    def __init__(self, id_, name, country, start_value, start_gdp):
        if not id_:
            raise Exception("Oooops")
            #
            # # имя игрока, нз зачем оно
            # self.name = name
            # # страна, выбранная игроком
            # self.country = country
            # # стартовый капитал и ввп, выдаваемые в соответствии с выбранной страной
            # # fund - это в пересчете на среднее значение валютного курса всех сбережений
            # self.fund = 0
            # # динамический gdp - сделано
            # self.start_gdp = start_gdp
            # # список юнитов (объектов класса Unit)
            # self.units = []
            # # сохраненние данных
            # '''
            # random.seed()
            # self.id_ = str(random.randint(1, 100))
            # '''
            #
            # self.value = {self.id_: start_value}

        # todo: тут нао добавить сохранение нового поля start_gdp и gdp
        # start_gdp - это изначально значение gdp у игрока
        # gdp - это последне значение ddp
        # если игрок уже заходил в эту сессию, то он переподключается за себя же
        elif id_ and not name and not country and not start_value and not start_gdp:
            self.id = id_
            # опять сохраняет данные для игрока
            user_data = pg_conn.get_data(id_)
            self.name = user_data[1]
            self.country = user_data[2]
            self.value = {id_: user_data[3]} if isinstance(user_data[3], int) else user_data[3]
            self.start_gdp = user_data[4]
            self.gdp = user_data[4]
            units_data = mongo_conn.get_units(id_)
            self.units = []
            for unit_data in units_data:
                self.units.append(Unit(data=unit_data))
        else:
            self.id = id_
            self.name = name
            self.country = country
            self.gdp = start_gdp
            self.value = {id_: start_value} if isinstance(start_value, int) else start_value
            units_data = mongo_conn.get_units(id_)
            self.units = []
            for unit_data in units_data:
                self.units.append(Unit(data=unit_data))

    def to_dict(self):
        dict_ = self.__dict__
        dict_['units'] = [unit.to_dict() for unit in self.units]
        return dict_

    def save(self):
        dict_ = copy.deepcopy(self.__dict__)
        dict_.pop("unit")
        pg_conn.update_data(dict_)

    def get_default_val(self, uid, country):
        return {uid: self.country_st[country][0]}, self.country_st[country][1]

    # удаление юнита при уничтожении
    def remove_unit(self, unit):
        self.units.remove(unit)

    # продажа юнита и отправка его в exchange
    # деньги придут, только когда этот юнит купят
    def sell_unit(self, unit):
        game.exchange.add_unit(unit, self)

    # покупка юнита у 'who'( - тот объект, что вызвал функцию (market или exchange))
    # если у игрока не хватает своей валюты для покупки юнита, то тратятся резервы
    # валют других стран
    # если же денег не хватает и так, то не происходит ничего
    def buy_unit(self, position, who):
        cost = who.units[position].cost
        if cost <= self.fund:
            if cost <= self.value[self.id] * game.new_rate[self.id]:
                self.value[self.id] -= round(cost / game.new_rate[self.id])
            else:
                cost -= round(self.value[self.id] * game.new_rate[self.id])
                self.value[self.id] = 0
                for id_ in game.players_id:
                    if id_ == self.id:
                        continue
                    if self.value[id_] * game.new_rate[id_] < cost:
                        self.value[id_] = 0
                        cost -= round(self.value[id_] * game.new_rate[id_])
                    else:
                        self.value[id_] -= round(cost * game.new_rate[id_])
                        break
            self.units.append(who.send_unit(position))
            if who == game.exchange:
                game.exchange.send_money(cost, position)

    def buy_value(self, value, id_):
        seller = game.players[game.players_id.index(id_)]
        self.value[seller.id] += value
        self.value[self.id] -= round(value * game.new_rate[seller.id] / game.new_rate[self.id])
        seller.value[seller.id] -= value

    # расчет прибыли в конце хода
    def calculate_profit(self):
        return sum([unit.productivity for unit in self.units if unit.steps == 0]) + (self.gdp * self.value[self.id])

    def calc_unit_profit(self):
        return sum([unit.productivity for unit in self.units if unit.steps == 0])

    # Todo: нз что ты тут написал
    # Несмотря на то, что это не ordered dict они всё ещё хранятся в порядке добавления, вроде как!!!
    def get_values(self):
        return list(self.__dict__.values())

    # подсчет тех огромных циферок в центре снизу экрана игрока
    # fund - это теперь пересчет всего капитала игрока (и его валюты и
    # чужой) в пересчете на среднее значение валюты
    def fund_calc(self, rate):
        values_ = []
        for id_ in game.players_id:
            if id_ not in  self.value.keys():
                continue
            values_.append(self.value[id_] * game.new_rate[id_])
        self.fund = sum(values_)
        return self.fund


class Unit(object):
    def __init__(self, id_, cost, steps, st_prod, level, data=None):
        if id_:
            data = mongo_conn.get_unit(id_)
        if data:
            for key, val in data.items():
                self.__setattr__(key, val)
                return

        # Todo: тут мы типа создаём unit? - да, но создается он в функциях других объектов
        #
        # задание полей id, кол-ва ходов для создания,
        # производительности, уровня, стоимости и создание id
        self.steps_to_create = steps
        self.steps = steps
        self.productivity_ = st_prod
        self.level = level
        self.cost = cost
        self.unit_id = mongo_conn.new_unit(self.__dict__)

    # поднятие уровня юнита
    # производится подсчет новых значений , основываясь на
    # файле unit.py - level_coef
    def lvl_up(self):
        self.level += 1
        self.productivity_ = round(self.productivity_ * level_coef[self.level - 1]['prod'])
        self.cost = round(self.cost * level_coef[self.level - 1]['prod'])
        mongo_conn.update_unit(self.unit_id, {'level': self.level, 'cost': self.cost, 'prod': self.productivity})

    def to_dict(self):
        return self.__dict__


# TODO: Senpai Nikita, notice me
# перед тем как создавать этот класс надо убедится что в players_, которое
# отправляется в game.__init__, были все нужные игроки
# больше сюда их во время игры добавлять не стоит
class Game(object):
    def __init__(self):
        self.players_id = []
        self.players = []
        # курс прошлого хода
        self.old_rate = {}
        # курс нового хода
        # отражает мощность создаваемого юнита, ведь через некоторое
        # кол-во ходов игрокам будет не хватать слабых начальных юнитов
        self.unit_char = 0
        self.players_rate = {}
        self.move = 0

        self.market = Market()
        self.exchange = Exchange()

    def start(self):
        for p in self.players:
            self.players_id.append(p.id)
        self.new_rate = self.rate_calc_first()


    # все действия для перехода на следующий ход
    def next_move(self):
        # выплата (ф-ия внитри этого класса)
        self.fund_move()

        # подсчет нового курса
        self.new_rate = self.rate_calc()

        # уменьшение кол-ва ходов до создания
        for p in self.players:
            for u in p.units:
                if u.steps > 0:
                    u.steps -= 1

        # уменьшения кол-ва ходов для уничтожения юнитов в объекстах
        # market и exchange
        # и сразу же проверка на непригодных
        for who in [self.market, self.exchange]:
            for i in range(len(who.time_exist)):
                who.time_exist[i] -= 1
            who.check()


        # сохранения
        # Todo: надо добавить сохранение сосотояния объектов market и exchange
        for p in self.players:
            p.save()
        self.save()


    # первый подсчет рейтинга
    def rate_calc_first(self):
        # тут тип надо сложить сумму всех фондов в собственной валюте игроков
        # а потом разделить значение одного на общее и распихать это все либо
        # в словарь, либо в список
        rate = {}
        sum_ = 0

        for p in self.players:
            sum_ += p.value[p.id]
        part = sum_ / len(self.players)
        for i in range(len(self.players)):
            rate.update({self.players_id[i]: (self.players[i].value[self.players_id[i]] / part)})

        return rate

    # последующие подсчеты
    def rate_calc(self):
        # а эта штука считает уже в последующие разы, когда надо учитывать сколько
        # у кого чужой валюты, причем чтобы было удобнее считать без рекурсивной хуйни,
        # можно использовать два поля old_rate и на его основании проводить подсчет
        self.old_rate = self.new_rate
        all_ = 0
        values = {}
        rate = {}
        for id_i in self.players_id:
            values.update({id_i: 0})
            for p in self.players:
                if id_i in p.value.keys():
                    values[id_i] += p.value[id_i]
                    all_ += p.value[id_i]

        for id_id in self.players_id:
            rate.update({id_id: round(values[id_id] / all_)})

        return rate

    # прибавлене в фонды в конце хода
    def fund_move(self):
        for p in self.players:
            p.value[p.id] += p.calculate_profit()

    # сохранение настроек игры
    def save(self):
        conn = PostgresConnection()
        conn.update_game_data(self.new_rate)
        pass

    # определение стадии игры для создания соответсвующих юнитов
    # подсчитывает среднее значение фондов и считает на сколько
    # производительные нужно создавать юниты
    def game_coef(self):
        coef_ = 0
        min_fund_value = min_value_percent * sum([p.fund for p in self.players]) / len(self.players)
        for i in range(len(unit_coef)):
            if min_fund_value > unit_coef[i]['prod']:
                coef_ += 1
        return coef_


# 'отцовский' класс для классов 'Market' и 'Exchange'
class UnitSell:
    # задание полей: список юнитов, их соответствующие продавцы (при
    # наличии) и время на существование
    def __init__(self):
        self.units = [None] * (4 * pages)
        self.seller = [None] * (4 * pages)
        self.time_exist = [1] * (4 * pages)

    # функция отправки юнита покупателю и возврат данных
    # о юните в классе Market или Exchange в исходное 'None'
    # состояние
    def send_unit(self, position):
        unit = self.units[position]
        self.units[position] = None
        self.time_exist = 1
        return unit


# сервер создает объект 'market' !именно такая "переменная"! класса
# Market
# класс хранит в себе все данные(
#
# они сохранены как объекты класса Unit в списке self.units,
# именно из этих классов надо будет доставать инфу и отправлять
# игроку, поэтому чекни нужные для вывода поля в классе Unit
#
# ), нужные для вывода в окно Exchange у игрока
# (их я пометил в файле logic.py в классе MarketExchangeUnits)
class Market(UnitSell):
    # создает юнитов, если их меньше нужного количества
    # и удаляет, если у них истекло время существования
    def check(self):
        for j in range(len(self.units)):
            if not self.units[j]:
                self.units[j] = self.create_unit()
                self.time_exist[j] = 5

            if self.time_exist[j] <= 0:
                self.time_exist[j] = 1
                self.units[j] = None

    # создание юнита на основе данных из файлы unit.py, рандомизирует
    # общий коэффициент rand_ и добавочную роизводительную мощь (для
    # самых везучих) и возвращает объект класса Unit
    def create_unit(self):
        coef_ = game.game_coef()
        random.seed()
        rand_ = random.randint(500, 1500)
        rand_adj = random.randint(1100, 1120)
        unit_c = rand_ / 1000
        cost_ = round(unit_coef[coef_]['cost'] * unit_c)
        steps = round(unit_coef[coef_]['steps'] * unit_c)
        st_prod = round(unit_coef[coef_]['prod'] * unit_c * rand_adj / 1000)
        unit = Unit(None, cost_, steps, st_prod, 1)
        return unit


# сервер создает объект 'exchange' !именно такая "переменная"! класса
# Exchange
# класс хранит в себе все данные(
#
# они сохранены как объекты класса Unit в списке self.units,
# именно из этих классов надо будет доставать инфу и отправлять
# игроку, поэтому чекни нужные для вывода поля в классе Unit
#
# ), нужные для вывода в окно Exchange у игрока
# (их я пометил в файле logic.py в классе MarketExchangeUnits)
class Exchange(UnitSell):
    # добавление юнита в Exchange, удаление его у игрока
    # сохранене данных (прописанных в отцовском классе) о юните
    # в полях объекта exchange
    def add_unit(self, unit, player):
        for i in range(len(self.units)):
            if not self.units[i]:
                self.units[i] = unit
                self.units[i].steps_to_create = unit.steps_to_create
                self.seller[i] = player
                self.time_exist[i] = 5
                break
        player.units.remove(unit)

    # отправляет деньги владельцу юнита
    # обнуляет все данные о юните, расположенном на i-той позиции
    def send_money(self, cost, position):
        self.seller[position].value[self.seller[position].id] += round(cost * game.new_rate[self.seller[position].id])
        self.seller[position] = None

    # проверка на уже залежавшиеся юниты
    # если таковые имеются, то они удаляются
    def check(self):
        for i in range(len(self.units)):
            if self.time_exist[i] <= 0:
                self.time_exist[i] = 1
                self.units[i] = None
                self.seller[i] = None


pg_conn = PostgresConnection()
mongo_conn = MongoConnection()

game = Game()

server = TcpServer()
server.run_()
