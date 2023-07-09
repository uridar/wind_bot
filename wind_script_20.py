import password_holder
import re
import mysql.connector
import datetime
import requests
from bs4 import BeautifulSoup
import time
import db_libary

get_users_db = "SELECT * FROM users"

url2 = 'https://www.windguru.net/int/iapi.php?q=live_update&lat=32.829&lon=35.513&WGCACHEABLE=30'
url1 = 'https://www.windguru.net/int/iapi.php?q=live_update&lat=32.83&lon=35&WGCACHEABLE=30'
url = 'https://www.windguru.net/int/iapi.php?q=live_update&lat=32.828&lon=35.513&WGCACHEABLE=30'

## dictionary mapping station IDs to their respective names.
id_to_bot_name = {'2049': 'בת גלים כנסיה', '2050': 'עכו', '2256': 'עתלית המבצר', '2763': 'שבי ציון', '1011': 'בצת',
                  '2259': 'שדות ים', '3377': 'נמל חדרה', '3808': 'שרונה','1909': 'כנרת מגדל', '2752': 'כנרת מצוף טבחה',
                  '3434': 'כנרת כפר נחום', '3379': 'כנרת בית צידה'}
staion_to_db = {'בת גלים כנסיה': 'bat_galim', 'בצת': 'bezet', "שדות ים": 'sdot_yam', 'עכו': 'ako', 'עתלית המבצר': 'atlit', 'שבי ציון': 'shavie_zion',
           'נמל חדרה':'hedera', 'שרונה': 'sarona', "כנרת מגדל": 'migdal', 'כנרת כפר נחום': 'kfar_nahom', 'כנרת בית צידה': 'beit_zida', 'כנרת מצוף טבחה': 'tabcha'}

#the bot token
TOKEN = password_holder.wind_bot_token

#the sql sentace to  pull the data from the db
get_users_sql = "SELECT * FROM users"
get_mes_sql = "SELECT * FROM station_get_mes "
get_mes_sql_id = "SELECT id FROM station_get_mes "


##########function that get the data from the windguru website
def get_staion_data(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    soup = str(soup)
    soup=soup.split('{')
    soup=soup[1::]
    staion_data=[]
    for i in soup:
        i=i.replace('"','')
        i=i.replace('}', '')
        i=i.replace('id_station:', '')
        i=i.split(',')
        if i[0] in id_to_bot_name.keys():
            replace_name = i[0]
            i[0] = id_to_bot_name[replace_name]
            i[1] = i[1].replace('unixtime:','')
            i[1] = datetime.datetime.fromtimestamp(int(i[1]))  # Unix Time
            i[1] = str(i[1])

            staion_data.append(i)
    return staion_data


# Define a function to reformat each item in the list
def format_wind_data(item_from_staion_data):
    # Extract the location name and date/time
    location = item_from_staion_data[0]
    date_time = item_from_staion_data[1]

    # Extract the various weather data points
    wind_avg_str = item_from_staion_data[2].split(":")[1]
    wind_max_str = item_from_staion_data[3].split(":")[1]
    wind_min_str = item_from_staion_data[4].split(":")[1]
    temperature_str = item_from_staion_data[5].split(":")[1]
    wind_direction_str = item_from_staion_data[6].split(":")[1]


    wind_avg = float(wind_avg_str) if wind_avg_str != "null" else 0
    wind_max = float(wind_max_str) if wind_max_str != "null" else 0
    wind_min = float(wind_min_str) if wind_min_str != "null" else 0


    # Construct a readable message string
    message = f"{location}\nTime: {date_time}\nAvg wind: {wind_avg_str} knots\nMax wind: {wind_max_str} knots\nMin wind: {wind_min_str} knots\nTemperature: {temperature_str} C\nWind direction: {wind_direction_str} degrees"

    return location,date_time, wind_avg, wind_max,message

#get spesifc chat id and all the data from the station_get_mes table and return the list of station that allready sent to this user
def staion_get_mes_3(chat_id, station_get_mes_db):
    staion_get_mes_user = []
    for user_staion in station_get_mes_db:
        if chat_id in user_staion:
            c = 0
            for staion in user_staion[1::]:
                if staion !=None:
                    staion_that_get_mes = list(staion_to_db.keys())[c]
                    staion_get_mes_user.append(staion_that_get_mes)
                c+=1
    return staion_get_mes_user
#get user id and text message and send it to him
def send_telegram_message(chat_id, message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    response = requests.get(telegram_url, params=params)
    # Handle response if needed

# the urls of the wind station
URLS = [url, url1, url2]

#a function that take location and wind speed and retrun all the ids from the users table that mach to it.
def get_id_to_mes(location, wind_avg, wind_max):
    id_to_send_mes = f"SELECT id FROM users WHERE {staion_to_db[location]}<{wind_avg} or {staion_to_db[location]}_max<{wind_max};"
    a=db_libary.db_get_s(id_to_send_mes)
    return a



def main():

    while True:
        ###### get the station_get_mes into list of lists
        get_mes_data = db_libary.db_get(get_mes_sql)
        print(get_mes_data)
        get_mes_dic = {}
        #run on all the get mes data and make a dictonary of {id:station_get_mes} and also delet the message that bin sent bofore more then 4 hours
        users_counter = 0
        for user in get_mes_data:
            counter = 0
            for timestamp in user:
                if type(timestamp)==datetime.datetime and (datetime.datetime.now()-timestamp).seconds>=14400:
                    a=None
                    get_mes_data[users_counter][counter]= a
                counter+=1
            station_get_mes_list = staion_get_mes_3(chat_id=get_mes_data[users_counter][0],
                                                    station_get_mes_db=get_mes_data)
            get_mes_dic[get_mes_data[users_counter][0]] = station_get_mes_list
            users_counter += 1

# the fuction run between 22 to 4:30 am
        current_time = datetime.datetime.now()
        if current_time.hour >= 22 or current_time.hour < 4:
            time.sleep(23400)  # Sleep for 6 hours and 30 minutes
            continue


        # Fetch station data
        list_of_station_data = []
        for url in URLS:
            data = get_staion_data(url)
            if data:
                list_of_station_data.extend(data)
#remove duplicate in data
        list_of_station_data1 =[]
        for data in list_of_station_data:
            if data not in list_of_station_data1:
                list_of_station_data1.append(data)
        #get every value on the station in different varible
        for item in list_of_station_data1:
            location, date_time, wind_avg, wind_max, message = format_wind_data(item)
            #insert all the ids that need to get mes into a list
            ids_to_get_mes= get_id_to_mes(location=location, wind_avg=wind_avg, wind_max=wind_max)
            for id in ids_to_get_mes:
                string = str(id)
                # Remove non-digit characters using regular expressions
                chat_id = re.sub(r'\D', '', string)
                #chack if the station isall ready get mes
                if location in get_mes_dic[chat_id]:
                    continue
                #if not send mes to the user and put the station in the station_that_get_mes table
                else:
                    if db_libary.db_update_get_mes(chat_id, staion_to_db[location]):
                        send_telegram_message(chat_id, message)
        print('End code')
        time.sleep(180)

while True:
    try:
        if __name__ == '__main__':
            main()
    except:
        continue



