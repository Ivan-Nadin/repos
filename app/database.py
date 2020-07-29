import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE







def create_database(user,password,host,port,existing_database,new_database):

    try:
        #connect to database
        conn = psycopg2.connect  (user = user,
                                  password = password,
                                  host = host,
                                  port = port,
                                  database = existing_database)

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        #checking if a database with this name exists in the list of Postgres databases
        exists=check_record_table(conn,'pg_catalog.pg_database','datname',"'"+new_database+"'")
        if not exists:
            cursor=conn.cursor()
            cursor.execute(f'CREATE DATABASE {new_database}')
            cursor.close()
            conn.close()
            print ("Successfully created a new database")
        else:
            print(f'Database {new_database} already exists')

    except (Exception, psycopg2.Error) as error :
        print('Failed for creating a new database', error)



sql_create_update_files='''
CREATE TABLE IF NOT EXISTS update_files
(
    update_id      bigint NOT NULL,
    file_id        varchar(450) NOT NULL,
    content_file   bytea NOT NULL,
    type_file      int NOT NULL,
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
CREATE TABLE IF NOT EXISTS description_type_file
(
    type_file      int NOT NULL,
    description     varchar(50)  NULL,
    PRIMARY KEY (type_file)
)
'''

sql_insert_type_file='''
 INSERT INTO description_type_file (type_file, description)
    VALUES  (0,'text_message')
           ,(1,'photo_message')
           ,(2,'voice_message')

'''


def create_tables(user,password,host,port,new_database):
    try:

        conn = psycopg2.connect  (user = user,
                                  password = password,
                                  host = host,
                                  port = port,
                                  database = new_database)

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor=conn.cursor()
        for sql in [sql_create_update_files,sql_create_update_info,sql_create_chat_info,sql_create_type_file,sql_insert_type_file]:
            cursor.execute(sql)
        cursor.close()
        print (f"Successfully created a tables in  {new_database} database")
        return conn
    except (Exception, psycopg2.Error) as error :
        print('Failed for creating a new tables', error)







def check_record_table(conn,table,column,value):
    cursor = conn.cursor()
    postgres_select_query=f""" select 1 from  {table} where {column} = {value} """
    cursor.execute(postgres_select_query)
    exists = cursor.fetchone()
    cursor.close()
    return exists



def insert_into_chat_info(conn,chat_id,first_name,last_name,is_bot):
    cursor = conn.cursor()
    postgres_insert_query = """ INSERT INTO chat_info (chat_id, first_name,last_name,is_bot)
                                VALUES (%s,%s,%s,%s)"""
    record_to_insert = (chat_id, first_name,last_name,is_bot)
    cursor.execute(postgres_insert_query, record_to_insert)
    cursor.close()




def insert_into_update_info(conn,update_id,message_id,date,chat_id):
    cursor = conn.cursor()
    postgres_insert_query = """ INSERT INTO update_info (update_id, message_id,date,chat_id)
                                VALUES (%s,%s,%s,%s)"""
    record_to_insert = (update_id, message_id,date,chat_id)
    cursor.execute(postgres_insert_query, record_to_insert)
    cursor.close()




def insert_into_update_files(conn,update_id,file_id,file,type):
    cursor = conn.cursor()
    postgres_insert_query = """ INSERT INTO update_files (update_id, file_id,content_file,type_file)
                                VALUES (%s,%s,%s,%s)"""
    record_to_insert = (update_id, file_id,file,type)
    cursor.execute(postgres_insert_query, record_to_insert)
    cursor.close()


    #data['message']['photo'][-1]['file_size']
