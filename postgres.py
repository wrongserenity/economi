import psycopg2
import logging

# TODO: add try:.. except... wrappers
class PostgresConnection:
    def __init__(self, configs):
        try:
            self.__conn = pg.connect(**configs)
        except pg.Error as e:
            logging.critical("%s occurred while connecting PostgreSQL Database" % str(e))
    
    def cursor(self):
        return self.__conn.cur()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__conn.commit()
        except pg.Error as e:
            logging.critical("%s occurred, can\'t save data, changes would be reverted" % str(e))
        self.__conn.close()
        
    # TODO: what outcome datatype is needed?
    def get_data(self, user_id):
        with self.cursor() as cur:
            cur.execute("FROM users_table SELECT * WHERE user_id = %d", (user_id, ))
            
    def get_many(self, user_id_list):
        with self.cursor() as cur:
            cur.prepare("FROM users_table SELECT * WHERE user_id = %d")
            for user_id in user_id_list:
                cur.execute(user_id)
                
    # TODO: update number of values
    # TODO: should return dict
    def set_data(self, user_obj):
        with self.cursor() as cur:
            cur.execute("INSERT INTO users_table VALUES (%s, %s, %s, %s)", (user_obj.get_values())
                    
