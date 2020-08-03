Test Telegram Bot
=============================


USAGE
------------

+ **OS** : Linux Mint 20 Ulyana
+ **Language** : Python 3.8.2
+ **Server** : localhost
+ **Database** : PostgreSQL 12.2 



Launch Bot
------------

In order to use method of Telegram API called webhooks ( for getting updates about input messages to the bot), necessary  deploy it on secure webserver with HTTPS. I used ngrok -  allows  to expose a web server running on your local machine to the internet. It can be downloaded on website <https://ngrok.com/download> .

The bot itself is launched by the command : ***python app/main.py [token] [server] [user_db] [password_db]***

- ***[token]*** - Authentication bot's token got from Telegram API
- ***[server]*** -  Server where  bot  will be deployed 
- ***[user_db]*** -  User of  Postgres Database
- ***[password_db]*** - Password of Postgres Database


Except this arguments, there are some optional . Command   ***python app/main.py --help***  will show description of all script's commands 

The algorithm of the bot
------------

Waiting for a POST-request from Telegram API.

After receiving it, bot checks what is contained in the message.

If this  message is photo , then it is checked for faces and sent phot  back to the user ( the faces are highlighted in the photo).

Another case, message is  the voice from user, then it is converted to wav format and bot sent audio also back it  to the user.

If message is a different view  then  bot send the text message with asking to send a photo or audio.

In addition, data is being written to the database, basic information about the received update, the message content (text, audio, photo(only containing faces))


Example
------------

Can view the  video of bot work in the file `example_work.mp4`

In file `telebot_db.ipynb` working with database dumps and examples of how to export and import data from a database






