#~/ngrok http 5000
# https://api.telegram.org/bot1364390634:AAE88BzBzOJKx_E4BN0tLDUtC6KkGSl9yU4/deletewebhook
# https://api.telegram.org/bot1364390634:AAE88BzBzOJKx_E4BN0tLDUtC6KkGSl9yU4/setWebhook?url= https://a8409f81dc3b.ngrok.io
# sudo apt-get install postgresql




from flask import Flask
from flask import request
from flask import jsonify
from datetime import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import requests
import json
import psycopg2
import argparse

#my modules
from face import detect_face
from database import insert_into_update_files,insert_into_update_info,insert_into_chat_info,check_record_table,create_database,create_tables
from voice import convert_audio



parser = argparse.ArgumentParser(description='Launch telegram bot')
parser.add_argument('token', type=str, help='Authentication token for bot')
parser.add_argument('user', type=str, default='postgres',help='User for connecting to Postgres Database')
parser.add_argument('password', type=str, default='1',help='Password for connecting to Postgres Database')
parser.add_argument('--host', type=str, default='localhost',help='Host for launching Postgres Database')
parser.add_argument('--port', type=str, default='5432',help='Port for launching Postgres Database')
parser.add_argument('--existing_database', type=str,default='postgres' , help='Name of Existing Postgres Database')
parser.add_argument('--new_database', type=str,default='telebot_db' , help='Name of Existing Postgres Database')
args = parser.parse_args()

token = args.token
user=args.user
password=args.password
host=args.host
port=args.port
existing_database=args.existing_database
new_database=args.new_database


create_database(user,password,host,port,existing_database,new_database)

conn=create_tables(user,password,host,port,new_database)


URL=f'https://api.telegram.org/bot{token}/'
URL_FILE='https://api.telegram.org/file/bot1364390634:AAE88BzBzOJKx_E4BN0tLDUtC6KkGSl9yU4/'
app = Flask(__name__) # link on current file (main.py)



def write_json(data,filename='answer.json'):
    with open(filename,'w') as file:
        json.dump(data,file,indent=2,ensure_ascii=False)


def send_message(chat_id,type_message,text=None,file=None,caption=None):
    url = URL + f'send{type_message}?chat_id={chat_id}'
    files = {type_message: file}
    answer = { 'text': text
              ,'caption' : caption}
    r = requests.post(url, data=answer,files=files)
    return r.json()


def get_file_content(file_id):
    url_file_path=URL+f'getFile?file_id={file_id}'
    r_file_path = requests.get(url_file_path).json()
    file_path=r_file_path['result']['file_path']
    url_file=URL_FILE+file_path
    r_file=requests.get(url_file)
    return r_file.content



@app.route('/', methods = ['POST','GET'])
def index(): # flask's view must send object
    if request.method == 'POST':
        r = request.get_json()
        #write_json(r)
        chat_id = r['message']['chat']['id']
        update_id=r['update_id']
        message_id = r['message']['message_id']
        ts_unix = int(r['message']['date'])
        date=datetime.utcfromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S')
        first_name = r['message']['chat']['first_name']
        last_name = r['message']['chat']['last_name']
        is_bot = r['message']['from']['is_bot']

        exists = check_record_table(conn,'update_info','update_id',update_id)
        if not exists:
            insert_into_update_info(conn,update_id,message_id,date,chat_id)

            exists = check_record_table(conn,'chat_info','chat_id',chat_id)
            if not exists:
                insert_into_chat_info(conn,chat_id,first_name,last_name,is_bot)


            if 'text' in r['message'].keys():
                #write_json(r,'text.json')
                text_content=r['message']['text']
                insert_into_update_files(conn,update_id,'a',text_content,'0') # запись аудио в БД
                send_message(chat_id,'message','Отправь мне аудио-сообщения или фото')
            elif 'photo' in r['message'].keys():
                write_json(r,'photo.json')
                last_file_id=r['message']['photo'][-1]['file_id']
                image_content=get_file_content(last_file_id)
                face_image,count=detect_face(image_content)
                #write_json(r1)
                phrase=f'Найдено лиц в количестве {count}'
                send_message(chat_id,'photo',file=face_image,caption=phrase)
                if count>0:
                    insert_into_update_files(conn,update_id,last_file_id,image_content,'1') # запись аудио в БД

            elif 'voice' in r['message'].keys():
                last_file_id=r['message']['voice']['file_id']
                voice_content=get_file_content(last_file_id) # аудио полученное от пользователя
                voice_content_wav16=convert_audio(voice_content)
                send_message(chat_id,'audio',file=voice_content_wav16) # отправка преобразованного аудио пользователю
                insert_into_update_files(conn,update_id,last_file_id,voice_content,'2') # запись аудио в БД


            return jsonify(r)
    return '<h1>Bot welcomes you</h1>'



if __name__ == "__main__":
    #main()
    app.run()
