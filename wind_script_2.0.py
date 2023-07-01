import pickle
import datetime
import requests
from bs4 import BeautifulSoup
import time
url2 = 'https://www.windguru.net/int/iapi.php?q=live_update&lat=32.829&lon=35.513&WGCACHEABLE=30'
url1 = 'https://www.windguru.net/int/iapi.php?q=live_update&lat=32.83&lon=35&WGCACHEABLE=30'
url = 'https://www.windguru.net/int/iapi.php?q=live_update&lat=32.828&lon=35.513&WGCACHEABLE=30'

## dictionary mapping station IDs to their respective names.
id_to_bot_name = {'2049': 'בת גלים כנסיה', '2050': 'עכו', '2256': 'עתלית המבצר', '2763': 'שבי ציון', '1011': 'בצת', '2259': 'שדות ים', '3377': 'נמל חדרה', '3808': 'שרונה', '1909': 'כנרת מגדל', '2752': 'כנרת מצוף טבחה', '3434': 'כנרת כפר נחום', '3379': 'כנרת בית צידה'}

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


TOKEN = "6108637814:AAFSs4JhYcgAD0IQ42rm61ttHS9WQ4ib0F4"
chat_id = "5649994619"


##########
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
##########


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




file_name = 'users_data.pkl'
file_name_script = 'users_data_script.pkl'

def users_dic_get():

    with open(file_name, 'r+b') as file:
        users_dic = pickle.load(file)
        file.close()
        return users_dic

def users_dic_script_get():
    with open(file_name_script, 'r+b') as file:
        users_dic_script = pickle.load(file)
        file.close()
        return users_dic_script

def users_dic_script_update(users_dic_script):
    with open(file_name_script, 'w+b') as file:
        pickle.dump(users_dic_script, file)
        file.close()


def send_telegram_message(chat_id, message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    response = requests.get(telegram_url, params=params)
    # Handle response if needed



URLS = [url, url1, url2]


def main():
    while True:
        current_time = datetime.datetime.now()

        if current_time.hour >= 22 or current_time.hour < 4 or (current_time.hour == 4 and current_time.minute < 30):
            users_dic_script = users_dic_get()
            users_dic_script_update(users_dic_script)
            time.sleep(23400)  # Sleep for 6 hours and 30 minutes
            continue

        users_dic = users_dic_get()
        users_dic_script = users_dic_script_get()
        # Check for new user registrations
        if set(users_dic.keys()) - set(users_dic_script.keys()):
            for key in users_dic:
                if key not in users_dic_script:
                    users_dic_script[key] = users_dic[key]
            users_dic_script_update(users_dic_script)


        # Fetch station data
        list_a_b = []
        for url in URLS:
            data = get_staion_data(url)
            if data:
                list_a_b.extend(data)

        for item in list_a_b:
            location, date_time, wind_avg, wind_max, message = format_wind_data(item)
            for user_id in users_dic:
                user = users_dic[user_id]
                if user.user_stage == 5 and location in user.station_to_get_update and location not in users_dic_script[user_id].station_that_get_mes:
                    if wind_avg > user.wind_to_alert_knots or wind_max > user.wind_to_alert_max:
                        send_telegram_message(user_id, message)
                        users_dic_script[user_id].station_that_get_mes[location] = datetime.datetime.now()
        users_dic_script_update(users_dic_script)

        # Clean up station data that has been sent to users
        for user_id in users_dic_script:
            user = users_dic_script[user_id]
            for station_name in list(user.station_that_get_mes.keys()):
                timestamp = user.station_that_get_mes[station_name]
                if (timestamp.hour + 4) <= current_time.hour and timestamp.minute <= current_time.minute:
                    del user.station_that_get_mes[station_name]
                    users_dic_script_update(users_dic_script)



        for user_id in users_dic_script:
            print(vars(users_dic_script[user_id]))
        print('End code')
        time.sleep(19)

while True:
    try:
        if __name__ == '__main__':
            main()
    except:
        continue