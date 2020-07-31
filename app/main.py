# ~/ngrok http 5000
# sudo apt-get install postgresql
# source venv/bin/activate
# pkill -9 -f main.py
# connect to postgres console
# 1.sudo -u postgres psql
# 2. \c db_name   this command for connect to  Database
# 3 \dt           this command show list of tables in Database


#-------Import necessary packages-------#
from flask import Flask
from flask import request
from flask import jsonify
from datetime import datetime
import requests
import json
import argparse

from database import *
from telebot import Telebot

#-------Create module for handling command line arguments (for launching bot)-------#
#https://habr.com/ru/company/ruvds/blog/440654/
parser = argparse.ArgumentParser(description = 'Launch telegram bot')
parser.add_argument('token', type = str, help='Authentication token for bot')
parser.add_argument('server', type = str, help = 'Server for deploy telegram bot ')
parser.add_argument('user_db', type = str, help = 'User for connecting to Postgres Database')
parser.add_argument('password_db', type = str,help = 'Password for connecting to Postgres Database')
parser.add_argument('--host_db', type = str, default='localhost',help = 'Host for launching Postgres Database')
parser.add_argument('--port_db', type = str, default = '5432',help = 'Port for launching Postgres Database')
parser.add_argument('--system_database', type = str,default='postgres' , help = 'Name of System Default Postgres Database')
parser.add_argument('--telebot_database', type = str,default='telebot_db' , help = 'Name of Postgres Database for Telegram Bot')
args = parser.parse_args() # parsing getting arguments

#-------Definition main variables-------#
token = args.token
server = args.server
user_db = args.user_db
password_db = args.password_db
host_db = args.host_db
port_db = args.port_db
system_database = args.system_database
telebot_database = args.telebot_database

#-------Work with system default posgres database-------#
with  System_Database(user_db,password_db,host_db,port_db,system_database) as s_db: # create object database

    # https://stackoverflow.com/questions/44511958/python-postgresql-create-database-if-not-exists-is-error
    exists = s_db.check_record_table('pg_catalog.pg_database','datname',"'"+telebot_database+"'") #checking for existense database which wish to create
    if not exists:
       s_db.create_database(telebot_database) # create database for storing bot data




app = Flask(__name__) # link on current file (main.py)

# helper function for viewing response telegram API
def write_json(data,filename = 'answer.json'):
    with open(filename,'w') as file:
        json.dump(data,file,indent = 2,ensure_ascii=False)


@app.route('/', methods = ['POST','GET']) # root directory
def index(): # flask's view must send object
    if request.method == 'POST':
        r = request.get_json() # webhooks telegram
        in_message = r['message'] # incoming message from user
        #write_json(r)

        #-------Main update info-------#
        chat_id = in_message['chat']['id']
        update_id = r['update_id']
        message_id = in_message['message_id']
        ts_unix = int(in_message['date'])
        date = datetime.utcfromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S')
        first_name = in_message['chat']['first_name']
        last_name = in_message['chat']['last_name']
        is_bot = in_message['from']['is_bot']


        #-------Storing basic information about messages to the bot-------#
        exists = t_db.check_record_table('update_info','update_id',update_id) # checking whether there is a response to such an update
        if not exists:
            t_db.insert_into_update_info(update_id,message_id,date,chat_id) # record about update in db

            exists = t_db.check_record_table('chat_info','chat_id',chat_id) #checking is this a new chat for our bot?
            if not exists:
                t_db.insert_into_chat_info(chat_id,first_name,last_name,is_bot) # record about chat in db

            #-------Choosing a bot's response to a user message-------#
            if 'text' in in_message.keys():
                #write_json(r,'text.json')
                in_text = r['message']['text']
                t_db.insert_into_update_files(update_id,in_text,None,None,'0') # record input text in db
                bot.send_message(chat_id,'message','Please send me a voice message or photos') # send response user
            elif 'photo' in in_message.keys():
                #write_json(r,'photo.json')
                last_file_id = r['message']['photo'][-1]['file_id'] # file id to find the file location
                if 'caption' in in_message.keys(): # checking if user attached text to photo
                    in_text = in_message['caption']
                else:
                    in_text = None
                photo_original,photo_face,count_face = bot.detect_face(last_file_id) # get photo from telegram server  and find face on photo
                bot.send_message(chat_id,'photo',file = photo_face,caption = f'Number of faces recognized : {count_face}') # send response user
                if count_face > 0: # storage if at least found one face
                    t_db.insert_into_update_files(update_id,in_text,last_file_id,photo_original,'1') # record input photo(sometimes else text) in db

            elif 'voice' in in_message.keys():
                #write_json(r,'voice.json')
                last_file_id = r['message']['voice']['file_id'] # file id to find the file location
                voice_original,voice_wav16 = bot.convert_voice(last_file_id) # get voice from telegram server  and convert it
                bot.send_message(chat_id,'audio',file = voice_wav16,caption = 'Your voice converted to WAV format with 16kHz') # send response user
                t_db.insert_into_update_files(update_id,None,last_file_id,voice_original,'2') # запись аудио в БД
            else:
                # if bot get another type of message
                bot.send_message(chat_id,'message','Please send me a voice message or photos')  # send response user


            return jsonify(r)
    return '<h1>Bot welcomes you</h1>'


# main program
if __name__ == "__main__":

    #-------Work with telegram bot database-------#
    with  Telebot_Database(user_db,password_db,host_db,port_db,telebot_database) as t_db: # create object database

        t_db.create_tables() # create data storage structure in database
        bot = Telebot(token,server) # create object Telegram Bot
        bot.setWebhook() # set webhook for getting updates from telegram
        app.run() # lauch flask application
