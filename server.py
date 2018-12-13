
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

import aiohttp
import config
from postgres import PostgresConnection
from mongo import MongoConnection
from unit import unit_coef, level_coef, pages, min_value_percent
import copy
# from for_server import game, market, exchange

import random
pg_conn = PostgresConnection()
mongo_conn = MongoConnection()

game = Game()


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

    def get_user_data(self, uid):
        game.players.append(Player(uid, None*4))
        if len(game.players) == 4:
            game.start()

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
        import pdb
        pdb.set_trace()
        return bytes(f"{json.dumps(obj)}\n", "utf-8") if out else json.loads(obj.decode("utf-8"))

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
                    data['args']['user_dict'].update({'value':value, "gdb": gdp})
                    out = self.set_user_data(data['args']['user_dict'])
                elif data['action'] == "update_user_data" and "user_dict" in data['args'].keys():
                    out = self.update_user_data(data['args']['user_dict'])
                elif data['action'] == "new_unit" and "unit_dict" in data['args'].keys():
                    out = self.new_unit(data['args']['unit_dict'])
                elif data['action'] == "update_unit" and "unit_id" in data['args'].keys() \
                        and "unit_dict" in data['args'].keys():
                    out = self.update_unit(data['args']['unit_id'], data['args']['unit_dict'])
                elif data["action"] == "get_uid":
                    out = self.postgres_connection.get_uid()
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
                  'German': [550, 1.12],
                  'China': [300, 1.25],
                  'Sweden': [500, 1.17]}

    def __init__(self, id_, name, country, ):
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
            self.id_ = id_
            # опять сохраняет данные для игрока
            user_data = pg_conn.get_data(id_)
            self.name = user_data[1]
            self.country = user_data[2]
            self.value = {id_: user_data[3]}
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
            self.value = {id_: start_value}

    def save(self):
        dict_ = copy.deepcopy(self.__dict__)
        dict_.pop("unit")
        pg_conn.update_data(dict_)

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
            if cost <= self.value[self.id_] * game.new_rate[self.id_]:
                self.value[self.id_] -= round(cost / game.new_rate[self.id_])
            else:
                cost -= round(self.value[self.id_] * game.new_rate[self.id_])
                self.value[self.id_] = 0
                for id_ in game.players_id:
                    if id_ == self.id_:
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
        self.value[seller.id_] += value
        self.value[self.id_] -= round(value * game.new_rate[seller.id_] / game.new_rate[self.id_])
        seller.value[seller.id_] -= value

    # расчет прибыли в конце хода
    def calculate_profit(self):
        return sum([unit.productivity for unit in self.units if unit.steps == 0]) + (self.gdp * self.value[self.id_])

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
        self.id_ = mongo_conn.new_unit(self.__dict__)

    # поднятие уровня юнита
    # производится подсчет новых значений , основываясь на
    # файле unit.py - level_coef
    def lvl_up(self):
        self.level += 1
        self.productivity_ = round(self.productivity_ * level_coef[self.level - 1]['prod'])
        self.cost = round(self.cost * level_coef[self.level - 1]['prod'])
        mongo_conn.update_unit(self.identifier, {'level': self.level, 'cost': self.cost, 'prod': self.productivity})

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
            self.players_id.append(p.id_)
        self.new_rate = self.rate_calc_first()

    # все действия для перехода на следующий ход
    def next_move(self):
        # выплата (ф-ия внитри этого класса)
        self.fund_move()

        # подсчет нового курса
        self.rate_calc()

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
            sum_ += p.value[p.id_]
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
                if p.value[id_i]:
                    values[id_i] += p.value[id_i]
                    all_ += p.value[id_i]

        for id_id in self.players_id:
            rate.update({id_id: round(values[id_id] / all_)})

        return rate

    # прибавлене в фонды в конце хода
    def fund_move(self):
        for p in self.players:
            p.value[p.id_] += p.calculate_profit()

    # сохранение настроек игры
    def save(self):
        # TODO: idk it's 5 am I wanna do that but i'm fallin' asleep, so, 2morro
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
        self.seller[position].value[self.seller[position].id_] += round(cost * game.new_rate[self.seller[position].id_])
        self.seller[position] = None

    # проверка на уже залежавшиеся юниты
    # если таковые имеются, то они удаляются
    def check(self):
        for i in range(len(self.units)):
            if self.time_exist[i] <= 0:
                self.time_exist[i] = 1
                self.units[i] = None
                self.seller[i] = None


'''
для вывода информации юнитов в окне у игрока надо отправлять соответствующие
данные из его класса (объекты класса Unit лежат в списке Player.units)
'''

'''
# пусть словари с данными игроков - это следующий список:
lst_player_data = [{'country': 'Russia', 'name': 'First'},
                   {'country': 'Sweden', 'name': 'Second'},
                   {'country': 'Russia', 'name': 'Third'},
                   {'country': 'China', 'name': 'Fourth'}]

players = []
for i in range(len(lst_player_data)):
    country = lst_player_data[i]['country']
    name = lst_player_data[i]['name']
    start_value = Player.country_st[country][0]
    start_gdp = Player.country_st[country][1]
    # здесь же определяем начальные значения для стран игроков
    # основываясь на их выбранной стране

    # Todo: сюда надо передать айдишник игрока
    id_ = None
    players.append(Player(id_, name, country, start_value, start_gdp))
'''
'''
game = Game(players)


units = []
id_ = None
cost = unit_coef[1]['cost']
steps = unit_coef[1]['steps']
prod = unit_coef[1]['prod']
level = unit_coef[1]['level']
unit = Unit(id_, cost, steps, prod, level)
game.players[0].units.append(unit)


print(game.__dict__)
print(game.players[0].__dict__)
print(game.players[0].units[0].__dict__)
game.players[0].units[0].lvl_up()
game.players[0].units[0].lvl_up()
game.players[0].units[0].lvl_up()

print(game.players[0].units[0].__dict__)
print(game.market.__dict__)
print(game.exchange.__dict__)

game.next_move()
game.next_move()

print('--------------')
print(game.__dict__)
print(game.players[0].__dict__)
print(game.players[0].units[0].__dict__)
print(game.players[0].units[0].__dict__)
print(game.market.__dict__)
print(game.exchange.__dict__)

print('------------')
game.players[0].sell_unit(game.players[0].units[0])
print(game.exchange.__dict__)
game.players[1].value[game.players_id[1]] = 100000
print('----')
print(game.players[1].units)
game.players[1].buy_unit(0, game.exchange)
print(game.players[1].units)
'''


server = TcpServer()
server.run_()





