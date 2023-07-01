import datetime
import requests
from bs4 import BeautifulSoup
import time
import pickle
import telebot
from telebot import TeleBot
from telebot import types

BOT_TOKEN = "6108637814:AAFSs4JhYcgAD0IQ42rm61ttHS9WQ4ib0F4"

class User:
    chat_ids_ = []
    golesh_count = 0

    def __init__(self, user_stage, chat_id, first_name, wind_to_alert_knots, wind_to_alert_max, station_to_get_update, station_that_get_mes):
        self.user_stage = user_stage
        self.chat_id = chat_id
        self.first_name = first_name
        self.wind_to_alert_knots = wind_to_alert_knots
        self.wind_to_alert_max = wind_to_alert_max
        self.station_to_get_update = station_to_get_update
        self.station_that_get_mes = station_that_get_mes
        self.chat_ids_.append(chat_id)
        User.golesh_count += 1

list_of_station = ['כנרת בית צידה', 'כנרת מגדל', 'בת גלים כנסיה', 'כנרת כפר נחום', 'כנרת מצוף טבחה', 'שרונה', 'בצת', 'נמל חדרה', 'עתלית המבצר', 'עכו', 'שבי ציון', 'שדות ים']
list_of_golshim = []

file_name = 'users_data.pkl'

def users_dic_get():
    try:
        with open(file_name, 'rb') as file:
            users_dic = pickle.load(file)
            file.close()
            return users_dic
    except FileNotFoundError:
        users_dic = {}
        return users_dic

def users_dic_update():
    with open(file_name, 'wb') as file:
        pickle.dump(users_dic, file)
        file.close()

users_dic = users_dic_get()

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['text'])
def welcome(message):
    users_dic_get()
    chat_id = message.chat.id
    first_name = message.chat.first_name
    user = users_dic.get(chat_id)

    if not user:
        bot.send_message(chat_id, text='ברוכים הבאים לווינד בוט להרשמה לחץ כן')

        users_dic[chat_id] = User(user_stage=0, chat_id=chat_id, first_name=first_name,
                                            wind_to_alert_knots=None, wind_to_alert_max=None, station_to_get_update= [], station_that_get_mes={})
        users_dic_update()

    user = users_dic[chat_id]

    if user.user_stage == 0 and message.text == 'כן':
        bot.send_message(chat_id, text='נרשמתם בהצלחה! שלחו מאיזה עוצמת רוח תרצו לקבל התראות')
        user.user_stage = 1
        users_dic_update()

    elif user.user_stage == 1:
        if message.text.isnumeric():
            wind_to_alert = int(message.text)
            bot.send_message(chat_id, text=f'תקבל הודעה מרוח של {message.text} קשרים')
            bot.send_message(chat_id, text='מאיזה עוצמת מכות רוח תרצו לקבל התראות')
            user.user_stage = 2
            user.wind_to_alert_knots = wind_to_alert
            users_dic_update()
        else:
            bot.send_message(chat_id, text='תשלח את תשובתך במספר לדוגמה: "14"')

    elif user.user_stage == 2:
        if message.text.isnumeric():
            wind_to_max = int(message.text)
            bot.send_message(chat_id, text=f'תקבל הודעה ממכות של {message.text} קשרים')
            user.user_stage = 4
            user.wind_to_alert_max = wind_to_max
            users_dic_update()
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
            users_dic_update()

        elif message.text in list_of_station:
            user.station_to_get_update.append(message.text)
            users_dic_update()

    elif user.user_stage == 5:
        if message.text == '_delete_':
            del users_dic[chat_id]
            users_dic_update()
        else:
            bot.send_message(chat_id, text='אתה כבר רשום לשירות. למחיקת המשתמש תשלח את ההודעה: _delete_')

    for user_id, user in users_dic.items():
        print(vars(user))

bot.infinity_polling()
