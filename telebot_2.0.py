import datetime
import requests
from bs4 import BeautifulSoup
import time
import pickle
import telebot
from telebot import TeleBot
from telebot import types
import mysql.connector
from mysql.connector import Error




BOT_TOKEN = "6108637814:AAFSs4JhYcgAD0IQ42rm61ttHS9WQ4ib0F4"

class User:
    chat_ids_ = []
    golesh_count = 0

    def __init__(self, user_stage, chat_id, first_name, wind_to_alert_knots, wind_to_alert_max, station_to_get_update):
        self.user_stage = user_stage
        self.chat_id = chat_id
        self.first_name = first_name
        self.wind_to_alert_knots = wind_to_alert_knots
        self.wind_to_alert_max = wind_to_alert_max
        self.station_to_get_update = station_to_get_update
        self.chat_ids_.append(chat_id)
        User.golesh_count += 1
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db')
        # open cursor, define and run query, fetch results
        cursor = conn.cursor()
        # Preparing SQL query to INSERT a record into the database.
        sql = "INSERT INTO users(id, firs_name,stage, station, wind, wind_max )"\
              "VALUES (%s, %s, %s, %s, %s, %s)"
        staff = (chat_id, first_name, user_stage, str(station_to_get_update), wind_to_alert_knots, wind_to_alert_max)
        try:
           # Executing the SQL command
            cursor.executem(sql, staff)
            # Commit your changes in the database
            conn.commit()
            sql ="SELECT * FROM users"
            cursor.execute(sql)
            r= cursor.fetchall()
            print(r)
        except:
            print('as')
            sql = "UPDATE users " \
                  "SET stage = %s ,station = %s, wind = %s, wind_max = %s " \
                  " WHERE id = " + str(chat_id) + ""
            staff = (user_stage, str(station_to_get_update), wind_to_alert_knots, wind_to_alert_max)
            # Executing the SQL command
            cursor.execute(sql, staff)
            # Commit your changes in the database
            conn.commit()

        # close the cursor and database connection
        cursor.close()
        conn.close()

list_of_station = ['כנרת בית צידה', 'כנרת מגדל', 'בת גלים כנסיה', 'כנרת כפר נחום', 'כנרת מצוף טבחה', 'שרונה', 'בצת', 'נמל חדרה', 'עתלית המבצר', 'עכו', 'שבי ציון', 'שדות ים']
list_of_golshim = []

def db_update(user_id):
    # try to run the block of code
    try:

        # establishing the connection
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db')

        # open cursor, define and run query, fetch results
        cursor = conn.cursor()
        # Preparing SQL query to INSERT a record into the database.
        sql = "INSERT INTO users(id)" "VALUES ("+user_id+")"

        try:
            # Executing the SQL command
            cursor.execute(sql)

            # Commit your changes in the database
            conn.commit()
            # close the cursor and database connection
            cursor.close()
            conn.close()
        except:
            print('the user id allready in the table')

    # catch exception and print error message
    except Error as err:
        print('Error message: ' + err.msg)

def db_get():
    # try to run the block of code
    try:

        # establishing the connection
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db')

        # open cursor, define and run query, fetch results
        cursor = conn.cursor()
        # Preparing SQL query to INSERT a record into the database.
        sql = "SELECT * FROM users"
           # Executing the SQL command
        cursor.execute(sql)
        result = cursor.fetchall()
        final_result = []
        for item in result:
            item = list(item)
            final_result.append(item)
        # close the cursor and database connection
        cursor.close()
        conn.close()
        return final_result
    # catch exception and print error message
    except Error as err:
        print('Error message: ' + err.msg)
        db_get()


users_dic = {}
bot = telebot.TeleBot(BOT_TOKEN)


file_name = 'users_data.pkl'
@bot.message_handler(content_types=['text'])
def welcome(message):

    chat_id = message.chat.id
    first_name = message.chat.first_name

    if chat_id not in User.chat_ids_:
        bot.send_message(chat_id, text='ברוכים הבאים לווינד בוט להרשמה לחץ כן')
        users_dic[chat_id] = User(user_stage=0, chat_id=chat_id, first_name=first_name,
                                            wind_to_alert_knots=0, wind_to_alert_max=0, station_to_get_update= [])

    user = users_dic[chat_id]

    if user.user_stage == 0 and message.text == 'כן':
        bot.send_message(chat_id, text='נרשמתם בהצלחה! שלחו מאיזה עוצמת רוח תרצו לקבל התראות')
        user.user_stage = 1


    elif user.user_stage == 1:
        if message.text.isnumeric():
            wind_to_alert = int(message.text)
            bot.send_message(chat_id, text=f'תקבל הודעה מרוח של {message.text} קשרים')
            bot.send_message(chat_id, text='מאיזה עוצמת מכות רוח תרצו לקבל התראות')
            user.user_stage = 2
            user.wind_to_alert_knots = wind_to_alert
        else:
            bot.send_message(chat_id, text='תשלח את תשובתך במספר לדוגמה: "14"')

    elif user.user_stage == 2:
        if message.text.isnumeric():
            wind_to_max = int(message.text)
            bot.send_message(chat_id, text=f'תקבל הודעה ממכות של {message.text} קשרים')
            user.user_stage = 4
            user.wind_to_alert_max = wind_to_max
            list_of_golshim.append(user)
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            buttons = [types.KeyboardButton(station) for station in list_of_station]
            buttons.append(types.KeyboardButton('סיימתי'))
            markup.add(*buttons)
            bot.send_message(chat_id, text='בחר תחנות לקבלת עדכונים, לסיום הקש סיימתי', reply_markup=markup)

        else:
            bot.send_message(chat_id, text='תשלח את תשובתך במספר לדוגמה: "14"')


    elif user.user_stage == 4:
        if message.text == 'סיימתי':
            stations = set(user.station_to_get_update)
            user.station_to_get_update = list(stations)
            user.user_stage = 5
            bot.send_message(chat_id, text='תהליך ההרשמה הסתיים בהצלחה, מהיום תקבל עדכוני רוח!')
            asd = User(user_stage=user.user_stage, chat_id= chat_id, first_name=first_name, wind_to_alert_knots=user.wind_to_alert_knots, wind_to_alert_max=user.wind_to_alert_max, station_to_get_update=user.station_to_get_update)
        elif message.text in list_of_station:
            user.station_to_get_update.append(message.text)

    elif user.user_stage == 5:
        if message.text == '_delete_':
            del users_dic[chat_id]
        else:
            bot.send_message(chat_id, text='אתה כבר רשום לשירות. למחיקת המשתמש תשלח את ההודעה: _delete_')

    for user_id, user in users_dic.items():
        print(vars(user))

bot.infinity_polling()
