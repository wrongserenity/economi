import sqlite3


class Player:
    """Class of counties"""
    def __init__(self, name, m_r_cur, st_fund):
        """Initiate starting parameters"""
        self.name = name                        # player's name
        self.main_ratio_currency = m_r_cur      # ratio to main currency
        self.fund = dict([(own, st_fund), (another_1, 0), (another_2, 0), (another_3, 0)])
        self.info_country = dict([(n, self.name), (s_m_r_c, self.main_ratio_currency), (f, self.fund)])   #
        # creating parameter dictionary of country

    def check_status(self):
        """Printing all information about country"""
        self.fund = self.count_fund()
        self.main_ratio_currency =
        self.info_country = dict([(n, self.name), (s_m_r_c, self.main_ratio_currency), (f, self.fund)])  #
        print(self.info_country)

    def count_fund(self):
        """Count fund of county"""
        return self.fund[own] + self.fund[another_1] * ratio_another_1 + self.fund[another_2] * ratio_another_2 + self.fund[another_3] * ratio_another_3

    def count_ratio(self):
        """Count ratio of country"""

    def purchase_currency_on_own(self, num_player, value, ratio):
        """Buying currency from another county"""

        self.fund += (self.fund[player[num_player]] - value) * player_ratio[num_player]

class Unit:
    pass


class Values:
    pass


player = {1: player1, 2: player2, 3: player3, 4: player4}

player_ratio = {a: 1 for a in range(1, 5)}
"""Setting ratio of players in start"""


player1 = Player()