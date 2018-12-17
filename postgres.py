import psycopg2 as pg
import logging
import json

# TODO: add try:.. except... wrappers
class PostgresConnection:
    def __init__(self, configs="dbname='postgres' user='postgres' host='localhost' password='12345678'"):
        try:
            self.__conn = pg.connect(configs)
        except pg.Error as e:
            logging.critical("%s occurred while connecting PostgreSQL Database" % str(e))
    
    def __cursor(self):
        return self.__conn.cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__conn.commit()
        except pg.Error as e:
            logging.critical("%s occurred, can\'t save data, changes would be reverted" % str(e))
        self.__conn.close()

    def update_game_data(self, rates):
        with self.__cursor() as cur:
            import pdb
            pdb.set_trace()
            if cur.execute("SELECT * FROM game_table"):
                cur.execute("UPDATE game_table SET rate = %s", json.dumps(rates))
            else:
                cur.execute("INSERT INTO game_table(rate) VALUES (%s)", json.dumps(rates))
        self.__conn.commit()

    def get_game_data(self):
        with self.__cursor() as cur:
            cur.execute("SELECT * FROM game_table")
            return cur.fetchone()
        
    # TODO: what outcome datatype is needed?
    def get_data(self, user_id):
        with self.__cursor() as cur:
            user_id = int(user_id) if isinstance(user_id, str) else user_id
            cur.execute("SELECT * FROM users_table WHERE id = %s", (user_id, ))
            res = cur.fetchone()
            if not res:
                return None
            res = list(res)
            res[0] = str(res[0])
            return res

    def get_uid(self):
        with self.__cursor() as cur:
            cur.execute("SELECT currval(pg_get_serial_sequence('users_table', 'id'))")
            res = cur.fetchone()
            return int(res) if res else 0

    def get_many(self, user_id_list):
        with self.__cursor() as cur:
            cur.prepare("FROM users_table SELECT * WHERE user_id = %d")
            for user_id in user_id_list:
                cur.execute(user_id)
                return cur.fetchall()
                
    # TODO: updatec number of values
    # TODO: should return dict
    def set_data(self, user_dict):
        with self.__cursor() as cur:
            val = user_dict['value']
            user_dict['value'] = json.dumps({'0': 1})
            cur.execute("INSERT INTO users_table(country, name, value, gdp) VALUES (%s, %s, %s, %s) RETURNING id", tuple(user_dict.values()))
            id_ = cur.fetchone()[0]
            cur.execute('UPDATE users_table SET value = %s WHERE id = %s',
                        (json.dumps({id_: val}), id_))
            self.__conn.commit()
            return id_

    def update_data(self, user_dict):
        with self.__cursor() as cur:
            id_ = user_dict.pop("id")
            cur.execute("UPDATE users_table SET name = %s, country = %s, value = %s, gdp = %s WHERE user_id = %s",
                        (*[val for val in user_dict.values()], id_))







