import psycopg2 as pg
import logging


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
        
    # TODO: what outcome datatype is needed?
    def get_data(self, user_id):
        with self.__cursor() as cur:
            user_id = int(user_id) if isinstance(user_id, str) else user_id
            cur.execute("SELECT * FROM users_table WHERE id = %s", (user_id, ))
            res = cur.fetchone()
            res[0] = int(res[0])
            return res

    def get_uid(self):
        with self.__cursor() as cur:
            cur.execute("SELECT max(id) from users_table")
            return int(cur.fetchone()[0])

    def get_many(self, user_id_list):
        with self.__cursor() as cur:
            cur.prepare("FROM users_table SELECT * WHERE user_id = %d")
            for user_id in user_id_list:
                cur.execute(user_id)
                return cur.fetchall()
                
    # TODO: update number of values     
    # TODO: should return dict
    def set_data(self, user_dict):
        with self.__cursor() as cur:
            cur.execute("INSERT INTO users_table(country, name, value, gdp) VALUES (%s, %s, %s, %s)", tuple(user_dict.values()))
            self.__conn.commit()
            return self.get_uid()

    def update_data(self, user_dict):
        with self.__cursor() as cur:
            id_ = user_dict.pop("id")
            cur.execute("UPDATE users_table SET name = %s, country = %s, value = %s, gdp = %s WHERE user_id = %s",
                        (*[val for val in user_dict.values()], id_))







