import db_libary
import re
import telebot
from telebot import types
import mysql.connector
from mysql.connector import Error
import password_holder
BOT_TOKEN = password_holder.wind_bot_token
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


staion_to_db = {'בת גלים כנסיה': 'bat_galim', 'בצת': 'bezet', "שדות ים": 'sdot_yam', 'עכו': 'ako',
                    'עתלית המבצר': 'atlit', 'שבי ציון': 'shavie_zion',
                    'נמל חדרה': 'hedera', 'שרונה': 'sarona', "כנרת מגדל": 'migdal', 'כנרת כפר נחום': 'kfar_nahom',
                    'כנרת בית צידה': 'beit_zida', 'כנרת מצוף טבחה': 'tabcha'}
list_of_station = ['כנרת בית צידה', 'כנרת מגדל', 'בת גלים כנסיה', 'כנרת כפר נחום', 'כנרת מצוף טבחה', 'שרונה', 'בצת', 'נמל חדרה', 'עתלית המבצר', 'עכו', 'שבי ציון', 'שדות ים']
list_of_golshim = []

sql = "SELECT id FROM users"
users_dic = {}
bot = telebot.TeleBot(BOT_TOKEN)

for id in db_libary.db_get(sql = "SELECT id FROM users"):
    string = str(id)
# Remove non-digit characters using regular expressions
    chat_id = re.sub(r'\D', '', string)
    users_dic[int(chat_id)] = User(user_stage=5, chat_id=int(chat_id), first_name=300,
                              wind_to_alert_knots=300, wind_to_alert_max=300, station_to_get_update=[])

@bot.message_handler(content_types=['text'])
def welcome(message):


    chat_id = message.chat.id
    first_name = message.chat.first_name
    print(chat_id)
    if chat_id not in users_dic.keys():
        print('as')
        bot.send_message(chat_id, text='ברוכים הבאים לווינד בוט להרשמה תכתוב כן')
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

#
    elif user.user_stage == 4:
        if message.text == 'סיימתי':
            stations = set(user.station_to_get_update)
            user.station_to_get_update = list(stations)
            new_list = []
            for station in user.station_to_get_update:
                station = staion_to_db[station]
                new_list.append(station)
            print(new_list)
            if db_libary.insert_numbers(user_id=chat_id, user_name=first_name, station_list=new_list,
            wind_to_alert_knots=user.wind_to_alert_knots, wind_to_alert_max=user.wind_to_alert_max) \
            and db_libary.db_update_get_mes(chat_id=chat_id, staion_name='id'):
                user.user_stage = 5
                bot.send_message(chat_id, text='תהליך ההרשמה הסתיים בהצלחה, מהיום תקבל עדכוני רוח!')

        elif message.text in list_of_station:
            user.station_to_get_update.append(message.text)


#delete the user for windbot_db
    elif user.user_stage == 5:
        if message.text == '_delete_':
            if db_libary.delete_row_by_id(chat_id, table_name='users'):
                db_libary.delete_row_by_id(chat_id, table_name='station_get_mes')
                del users_dic[chat_id]
                bot.send_message(chat_id, text='המשתמש נמחק בהצלחה מעכשיו לא תקבל עדכוני רוח')

        else:
            bot.send_message(chat_id, text='אתה כבר רשום לשירות. למחיקת המשתמש תשלח את ההודעה: _delete_')


bot.infinity_polling()
