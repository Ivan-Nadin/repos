
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE


sql_create_update_files='''
CREATE TABLE IF NOT EXISTS update_files
(
    update_id      bigint NOT NULL,
    text_message   bytea  NULL,
    file_id        varchar(450)  NULL,
    content_file   bytea  NULL,
    type_message      int NOT NULL,
    PRIMARY KEY (update_id)
)
'''

sql_create_update_info ='''
CREATE TABLE IF NOT EXISTS update_info
(
    update_id      bigint NOT NULL,
    message_id     bigint NOT NULL,
    date      timestamp NOT NULL,
    chat_id      bigint NOT NULL,
    PRIMARY KEY (update_id)
)
'''

sql_create_chat_info='''
CREATE TABLE IF NOT EXISTS chat_info
(
    chat_id      bigint NOT NULL,
    first_name     varchar(400)  NULL,
    last_name     varchar(400)  NULL,
    is_bot        Boolean      NOT NULL,
    PRIMARY KEY (chat_id)
)
'''


sql_create_type_file='''
CREATE TABLE IF NOT EXISTS description_type_message
(
    type_message      int NOT NULL,
    description     varchar(50)  NULL,
    PRIMARY KEY (type_message)
)
'''


#https://stackoverflow.com/questions/49939650/sql-insert-into-table-if-doesnt-have-data
sql_insert_type_file='''
 INSERT INTO description_type_message (type_message, description)
    SELECT t.type_message,t.description
    FROM (SELECT 0 as type_message,'text_message' as description   UNION ALL
          SELECT 1 as type_message,'photo_message' as description  UNION ALL
          SELECT 2 as type_message,'voice_message' as description
         ) t
    WHERE NOT EXISTS (SELECT * FROM description_type_message)

'''





class Postgres_DB(object):

    def __init__(self,user,password,host,port,database):
        self.user=user
        self.password=password
        self.host=host
        self.port=port
        self.database=database

    #https://www.psycopg.org/articles/2010/10/22/passing-connections-functions-using-decorator/
    #https://tproger.ru/translations/demystifying-decorators-in-python/
    def with_cursor(f):
        def with_cursor(self,*args):
            cursor=self.conn.cursor()
            args=tuple([item for item in args])
            try:
                f(self,cursor,*args)
            except (Exception, psycopg2.Error) as error :
                print ("Error while connecting to PostgreSQL", error)
            finally:
                cursor.close()
        return with_cursor


    #https://stackoverflow.com/questions/1984325/explaining-pythons-enter-and-exit
    #https://codereview.stackexchange.com/questions/213332/multiple-database-connections-class
    def __enter__(self):
        self.conn=psycopg2.connect(**self.db_config)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print(f'Connect is established to {self.database} database ')
        return self


    def check_record_table(self,table,column,value):
        cursor = self.conn.cursor()
        postgres_select_query=f""" select 1 from  {table} where {column} = {value} """
        cursor.execute(postgres_select_query)
        exists = cursor.fetchone()
        cursor.close()
        return exists

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print(f'Connect is closed to {self.database} database ')


#http://pythonicway.com/education/python-oop-themes/21-python-inheritance
#https://younglinux.info/oopython/inheritance.php
class System_Database(Postgres_DB):
    def __init__(self,user,password,host,port,database):
        #initialise the superclass
        super().__init__(user,password,host,port,database)
        self.db_config={'database':database,'host':host,'password':password,'port':port,'user':user}
        self.conn=None

    @Postgres_DB.with_cursor
    def create_database(self,cursor,*args):
        sql_create_database='CREATE DATABASE %s'
        cursor.execute(sql_create_database%args)
        print (f"Successfully created a {args[0]} database")


class Telebot_Database(Postgres_DB):
    def __init__(self,user,password,host,port,database):
        #initialise the superclass
        super().__init__(user,password,host,port,database)
        self.db_config={'database':database,'host':host,'password':password,'port':port,'user':user}
        self.conn=None

    @Postgres_DB.with_cursor
    def create_tables(self,cursor,*args):
        for sql in [sql_create_update_files,sql_create_update_info,sql_create_chat_info,sql_create_type_file,sql_insert_type_file]:
            cursor.execute(sql)
        print (f"Successfully created a tables in  {self.database} database")

    @Postgres_DB.with_cursor
    def insert_into_chat_info(self,cursor,*args):
        postgres_insert_query = """ INSERT INTO chat_info (chat_id, first_name,last_name,is_bot)
                                    VALUES (%s,%s,%s,%s)"""

        cursor.execute(postgres_insert_query,args)


    @Postgres_DB.with_cursor
    def insert_into_update_info(self,cursor,*args):
        postgres_insert_query = """ INSERT INTO update_info (update_id, message_id,date,chat_id)
                                    VALUES (%s,%s,%s,%s)"""

        cursor.execute(postgres_insert_query,args)

    @Postgres_DB.with_cursor
    def insert_into_update_files(self,cursor,*args):

        postgres_insert_query = """ INSERT INTO update_files (update_id, text_message,file_id,content_file,type_message)
                                    VALUES (%s,%s,%s,%s,%s)"""

        cursor.execute(postgres_insert_query,args)
