import sqlite3


class Player:
    """Class of players"""
    def __init__(self, id, name, m_r_cur, st_fund):
        """Initiate starting parameters: id, name, """
        self.id = id
        self.name = name                        # player's name
        self.ratio = float(count_ratio(id))      # ratio to main currency
        self.main_fund_old
        self.fund = dict([(id, st_fund), (abs(id - 1), 0), (abs(id - 2), 0), (abs(id - 3), 0)])     # dictionary of
        self.info_country = dict([(n, self.name), (s_m_r_c, self.main_ratio_currency), (f, self.fund)])   #
        # creating parameter dictionary of country

    def check_status(self):
        """Printing all information about country"""
        self.fund = self.count_fund()
         #
        print(self.info_country)

    def count_fund_new(self):
        """Count fund of county"""
        return sum(self.fund[i] * count_ratio_old[i] for i in range(1,5))


    def purchase_currency_on_own(self, num_player, value, ratio):
        """Buying currency from another county"""

        self.fund += (self.fund.[ - value) * player_ratio[num_player]

class Unit:
    pass



def count_ratio_new(id):


def count_ratio_for_n_player(id):
    half_sum = sum(main_fund_old[x] for x in range(1, 5)) / 2



main_fund_old = {1: 1.fund[1]}







player = {1: player1, 2: player2, 3: player3, 4: player4}

player_ratio = {a: 1 for a in range(1, 5)}
"""Setting ratio of players in start"""


player1 = Player()