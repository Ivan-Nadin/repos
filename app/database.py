#-------Import necessary packages-------#
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # https://www.psycopg.org/docs/extensions.html?highlight=isolation%20level#psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT


# install psycopg2 on younglinux
# https://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python

# tutorial psycopg2
#https://pynative.com/python-postgresql-tutorial/#:~:text=Use%20the%20connect()%20method,connection%20after%20your%20work%20completes.

# best practice for  working with database
#https://www.psycopg.org/docs/faq.html#best-practices

# examples of  sql query for work PostgreSQL
#https://kb.objectrocket.com/category/postgresql

#recommended using the singleton pattern for work with database
# https://softwareengineering.stackexchange.com/questions/200522/how-to-deal-with-database-connections-in-a-python-library-module
# another approach
# https://softwareengineering.stackexchange.com/questions/261933/using-one-database-connection-across-multiple-functions-in-python/291705


# parent class responsible for calling the connection, closing it,
# working with the cursor and checking the existence of records in the table
class Postgres_DB(object):

    def __init__(self,user,password,host,port,database):
        #initialization of parameters for connection
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    #https://www.psycopg.org/articles/2010/10/22/passing-connections-functions-using-decorator/
    #https://tproger.ru/translations/demystifying-decorators-in-python/
    # decorator for functions that contain an SQL request for execution
    #allows work with cursor (without fetch)
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
    #magic method allows to work with context manager
    def __enter__(self):
        self.conn=psycopg2.connect(**self.db_config) # create connection
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print(f'Connect is established to {self.database} database ')
        return self

    # function allows check record in table by column value
    def check_record_table(self,table,column,value):
        cursor = self.conn.cursor()
        postgres_select_query=f""" select 1 from  {table} where {column} = {value} """
        cursor.execute(postgres_select_query)
        exists = cursor.fetchone()
        cursor.close()
        return exists

    #magic method allows to work with context manager
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print(f'Connect is closed to {self.database} database ')


#http://pythonicway.com/education/python-oop-themes/21-python-inheritance
#https://younglinux.info/oopython/inheritance.php

# child class for work with default system
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

    #-------CRUD Operations in Database -------#

    @Postgres_DB.with_cursor
    def create_tables(self,cursor,*args):
        for sql in [sql_create_update_files,sql_create_update_info,sql_create_chat_info,sql_create_type_file,sql_insert_type_file]:
            cursor.execute(sql)
        print (f"Successfully created  tables in  {self.database} database")



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



#-------SQL query for creating structure in database-------#

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
