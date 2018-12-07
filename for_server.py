from classes import *
from country import *
from unit import *

import pdb

# пусть словари с данными игроков - это следующий список:
lst_player_data = [{'country': 'Russia', 'name': 'First'},
                   {'country': 'Sweden', 'name': 'Second'},
                   {'country': 'Russia', 'name': 'Third'},
                   {'country': 'China', 'name': 'Fourth'}]

players = []
for i in range(len(lst_player_data)):
    country = lst_player_data[i]['country']
    name = lst_player_data[i]['name']
    start_value = country_st[country][0]
    start_gdp = country_st[country][1]
    # здесь же определяем начальные значения для стран игроков
    # основываясь на их выбранной стране

    # Todo: сюда надо передать айдишник игрока
    id_ = None
    players.append(Player(id_, name, country, start_value, start_gdp))

game = Game(players)

moves = 5
while moves > 0:
    game.next_move()
    moves -= 1

units = []
id_ = None
cost = unit_coef[1]['cost']
steps = unit_coef[1]['steps']
prod = unit_coef[1]['prod']
level = unit_coef[1]['level']
unit = Unit(id_, cost, steps, prod, level)
game.players[0].plus_unit(cost, unit)

exchange = Exchange()
market = Market()

print(game.__dict__)
print(game.players[0].__dict__)
print(game.players[0].units[0].__dict__)
game.players[0].units[0].lvl_up()
print(game.players[0].units[0].__dict__)



