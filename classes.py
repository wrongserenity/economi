import sqlite3


class Player:
    """Class of players"""
    def __init__(self, p_id, nm, st_fund):
        """Initiate starting parameters: id, name, fund in starting"""
        self.player_id = p_id
        self.name = nm                        # player's name
        self.fund = st_fund
        self.units = {}

    def get_info(self):
        return {'id': self.player_id, 'name': self.name, 'units': self.units, 'fund': self.fund}

    def check_status(self):
        """Printing all information about country"""
        print(self.get_info)

    def start_making_unit(self):


    def creating_unit(self):
        pass


class Unit(self):
    """Created units by players"""
    def __init__(self, player_id):
        self.


class Market:
    pass








player = {1: player1, 2: player2, 3: player3, 4: player4}

player_ratio = {a: 1 for a in range(1, 5)}
"""Setting ratio of players in start"""


player1 = Player()
