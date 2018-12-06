import aiohttp
import config
from postgres import PostgresConnection
from mongo import MongoConnection
from unit import *
from country import *


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


class Player:
    def __init__(self, id_, name=None, country=None, units=None, start_fund=None, start_gdp=None, ):
        if not id_:
            # имя игрока, нз зачем оно
            self.name = name
            # страна, выбранная игроком
            self.country = country
            # стартовый капитал и ввп, выдаваемые в соответствии с выбранной страной
            self.fund = start_fund
            self.gdp = start_gdp
            # сохраненние данных
            PostgresConnection.set_data()
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

    def save(self):
        # хз шо с ентим делать, если честно
        PostgresConnection.set_data(user_obj)

    # прибавление в фонде при продаже юнита
    def income_fund(self, profit):
        self.fund += profit

    # вычитане из фонда при покупке юнита
    def outlay_fund(self, sum_):
        self.fund -= sum_

    # прибавление юнита
    def plus_unit(self, cost, ):
        self.fund -= cost
        self.count_units += 1
        self.units.append()

    # удаление юнита при пробдаже/уничтожении
    def minus_unit(self, cost):
        self.fund += cost
        self.count_units -= 1
        self.units
        pass

    # расчет прибыли в конце хода
    def calculate_profit(self):
        return sum([unit.productivity for unit in self.units]) + self.gdp
    
    # TODO: what about order?
    def get_values(self):
        return list(self.__dict__.values())


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
class Game:
    def __init__(self):
        # курс прошлого хода
        self.old_rate = {}
        # отражает мощность создаваемого юнита, ведь через некоторое
        # кол-во ходов игрокам будет не хватать слабых начальных юнитов
        self.unit_char = 0
        self.players = []
        self.players_rate = {}
        self.move = 0

        self.market = Market()

    # все действия для перехода на следующий ход
    def next_move(self):
        self.fund_move()
        for p in self.players:
            p.save()
        self.save()

    # первый подсчет рейтинга
    def rate_calc_first(self):
        # тут тип надо сложить сумму всех фондов в собственной валюте игроков
        # а потом разделить значение одного на общее и распихать это все либо
        # в словарь, либо в список
        for p in self.players:
            pass

    # последующие подсчеты
    def rate_calc(self, id_):
        # а эта штука считает уже в последующие разы, когда надо учитывать сколько
        # у кого чужой валюты, причем чтобы было удобнее считать без рекурсивной хуйни,
        # можно использовать два поля old_rate и на его основании проводить подсчет
        for p in self.players:
            pass

    # проверка на заполненность маркета и на отсутствие слишком слабых юнитов
    # оздает юнита в противном случае
    def market_check(self):
        while self.market.num_units < 4:
            self.market.create_unit(self.unit_char)

    # прибавлене в фонды в конце хода
    def fund_move(self):
        for p in self.players:
            p.income_fund(p.calculate_profit())

    # сохранение настроек игры
    def save(self):
        pass


# разберись с ентим дерьмом
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
