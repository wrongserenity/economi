import uuid
from mongo import MongoConnection
from postgres import PostgresConnection
from const import LVLUP


class Connection:
    def __init__(self):
        pass

    def load_settings(self):
        pass


class Player:
    def __init__(self, id_=None, name=None, country=None, units=None, start_fund=None, start_gdp=None, ):
        if not id_:
            id_ = uuid.uuid4()
            self.name = name
            self.country = country
            self.fund = start_fund
            self.gdp = start_gdp
            PostgresConnection.set_data(self)
            self.units = []
            return
        else:
            self.id_ = id_
            for key, val in get_data(self.id_).item():
                self.__setattr__(key, val)
            self.units = [Unit(data=data) for data in get_units(self.id_)]

    def save(self):
        set_data(self)

    def income_fund(self, profit):
        self.fund += profit

    def outlay_fund(self, sum_):
        self.fund -= sum_

    def plus_unit(self, cost, ):
        self.fund -= cost
        self.count_units += 1
        self.units.append()

    def minus_unit(self, cost):
        self.fund += cost
        self.count_units -= 1
        self.units
        pass

    def calculate_profit(self):
        return sum([unit.productivity for unit in self.units]) + gdp
    
    # TODO: what about order?
    def get_values(self):
        return list(self.__dict__.values())


class UnitMaker:
    def __init__(self):
        id_ = uuid.uuid4()


class Unit:
    def __init__(self, id_=None, cast_time=None, cast_cost=None, st_prod=None, data=None):
        if data:
            for key, val in data.items():
                self.__setattr__(key, val)
                return
        self.identifier = id_
        self.steps_to_create = cast_time
        self.productivity = st_prod
        self.cast_cost = cast_cost

    def lvl_up(self):
        self.level += 1
        self.productivity *= 1.0 + LVLUP
        MongoConnection.update_unit(self.identifier, {'level': self.level})

    def remove(self):
        MongoConnection.remove_unit(self.identifier)
    
    def to_dict(self):
        return self.__dict__
            

class Game:
    def __init__(self):
        pass

    def next_move(self, players):
        for p in players:
            p.income_fund(...)


class Market:
    def __init__(self):
        self.units_to_sell = {}
        self.units = {}         # разберись
    
    def buy(self):
        pass

    def sell(self):
        pass

    def process(self):
        pass
