import aiohttp
import config
from postgres import PostgresConnection
from mongo import MongoConnection
from unit import *
from country import *

import random


class Connection:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.base_ip = config.SERVER_IP
        self.base_port = config.SERVER_PORT
        self.get_id_url = f"{self.base_ip}:{self.base_port}/get_id"

    async def get_uid(self):
        async with self.session.get(self.get_id) as response:
            return await response.text()

    def load_settings(self):
        pass


class Player(object):
    def __init__(self, id_, name, country_, start_value, start_gdp):
        if not id_:
            # имя игрока, нз зачем оно
            self.name = name
            # страна, выбранная игроком
            self.country = country_
            # стартовый капитал и ввп, выдаваемые в соответствии с выбранной страной
            # Todo: надо разграничить понятие фонда в пересчете на общую валюту
            # путь fund - это в пересчете
            self.fund = 0
            self.gdp = start_gdp

            self.value = start_value
            self.other_country_value = {}

            # todo: временная чтука для проверки работоспособности
            self.id_ = str(random.randint(1, 8))
            # сохраненние данных
            # PostgresConnection.set_data()
            self.units = []
            return
        # если игрок уже заходил в эту сессию, то он переподключается за себя же
        else:
            self.id_ = id_
            # опять сохраняет данные для игрока
            # TODO: тут нз как get_data и get_units
            for key, val in PostgresConnection.get_data(self.id_).item():
                self.__setattr__(key, val)
            self.units = [Unit(data=data) for data in MongoConnection.get_units(self.id_)]

    # Todo: куда сохранять нз
    def save(self):
        # хз шо с ентим делать, если честно
        # PostgresConnection.set_data(user_obj)
        pass

    # прибавление в фонде при продаже юнита
    def income_value(self, profit):
        self.value += profit

    # вычитане из фонда при покупке юнита
    def outlay_value(self, sum_):
        self.value -= sum_

    # прибавление юнита
    def plus_unit(self, cost, unit):
        self.fund -= cost
        self.count_units += 1
        self.units.append(unit)

    # удаление юнита при пробдаже/уничтожении
    def minus_unit(self, cost, unit):
        self.fund += cost
        self.count_units -= 1
        self.units.remove(unit)
        pass

    # расчет прибыли в конце хода
    def calculate_profit(self):
        return sum([unit.productivity for unit in self.units]) + (self.gdp * self.value)
    
    # TODO: what about order?
    def get_values(self):
        return list(self.__dict__.values())

    def fund_calc(self, rate):
        values = []
        for key in self.other_country_value.keys():
            values.append(self.other_country_value[key] * rate[key])
        values.append(self.value * rate[self.id_])
        self.fund = sum(values)
        return self.fund


class Unit:
    def __init__(self, id_=None, cost=None, cast_time=None, cast_cost=None, st_prod=None, data=None, level=None):
        if data:
            for key, val in data.items():
                self.__setattr__(key, val)
                return
        # задание полей id, кол-ва ходов для создания,
        self.identifier = id_
        self.steps_to_create = cast_time
        self.productivity_ = st_prod
        self.cast_cost = cast_cost
        self.level = level
        self.productivity = 0
        self.cost = cost

    def lvl_up(self):
        self.level += 1
        self.productivity = round(self.productivity * level_coef[self.level - 1]['prod'])
        self.cost = round(self.cost * level_coef[self.level - 1]['prod'])
        MongoConnection.update_unit(self.identifier, {'level': self.level, 'cost': self.cost, 'prod': self.productivity})

    def remove(self):
        MongoConnection.remove_unit(self.identifier)
    
    def to_dict(self):
        return self.__dict__


# TODO: Senpai Nikita, notice me
class Game(object):
    def __init__(self, players_):
        self.players = players_
        self.players_id = []
        for p in self.players:
            self.players_id.append(p.id_)
        # курс прошлого хода
        self.old_rate = {}
        # курс нового хода
        self.new_rate = self.rate_calc_first()
        # отражает мощность создаваемого юнита, ведь через некоторое
        # кол-во ходов игрокам будет не хватать слабых начальных юнитов
        self.unit_char = 0
        self.players_rate = {}
        self.move = 0
        # Todo: надо сюда добавлять все айдишки игроков

        self.market = Market()
        self.exchange = Exchange()

        # TODO: check this
        self.game_start()

    # все действия для перехода на следующий ход
    def next_move(self):
        self.fund_move()
        for p in self.players:
            p.save()
        self.save()
        self.rate_calc()

    # Todo: check this
    # первый подсчет рейтинга
    def rate_calc_first(self):
        # тут тип надо сложить сумму всех фондов в собственной валюте игроков
        # а потом разделить значение одного на общее и распихать это все либо
        # в словарь, либо в список
        rate = {}
        sum_ = 0

        for p in self.players:
            sum_ += p.value
        part = sum_ / len(self.players)
        for i in range(len(self.players)):
            rate.update({self.players_id[i]: (self.players[i].value / part)})

        return rate

    # Todo: and this
    # последующие подсчеты
    def rate_calc(self):
        # а эта штука считает уже в последующие разы, когда надо учитывать сколько
        # у кого чужой валюты, причем чтобы было удобнее считать без рекурсивной хуйни,
        # можно использовать два поля old_rate и на его основании проводить подсчет
        self.old_rate = self.new_rate
        rate = {}
        sum_ = 0
        fund = []
        for i in range(len(self.players)):
            fund.append(self.players[i].fund_calc(self.old_rate))
        sum_ = sum(fund)
        for i in range(len(self.players)):
            rate.update({self.players[i].id_: (fund[i] / sum_)})
        return rate

    # проверка на заполненность маркета и на отсутствие слишком слабых юнитов
    # оздает юнита в противном случае
    def market_check(self):
        while self.market.num_units < 4:
            self.market.create_unit(self.unit_char)

    # прибавлене в фонды в конце хода
    def fund_move(self):
        for p in self.players:
            p.income_value(p.calculate_profit())

    # сохранение настроек игры
    def save(self):
        pass

    def game_start(self):
        self.new_rate = self.rate_calc_first()


# Todo: разберись с ентим дерьмом
class UnitSell:
    def __init__(self):
        self.units_to_sell = {}
        self.units = {}
        self.num_units = 0

    def buy(self):
        pass


class Market(UnitSell):
    def __init__(self):
        pass

    def process(self):
        pass

    def create_unit(self, unit_char):
        pass


class Exchange(UnitSell):
    def __init__(self):
        pass

    def sell(self):
        pass
