import mysql.connector
from mysql.connector import Error

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



def db_get_s(sql):
    try:
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db'
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as err:
        print('Error message: ' + err.msg)
        db_get(sql)



### get select * from table name string and return a list of all the table values.
def db_get(sql):
    try:
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db'
        )
        cursor = conn.cursor()

        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        result_final = []
        for user in result:
            user = list(user)
            result_final.append(user)
        return result_final
    except mysql.connector.Error as err:
        print('Error message: ' + err.msg)
        db_get(sql)




def db_update_get_mes(chat_id, staion_name):
    # try to run the block of code
    try:
        # establishing the connection
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db')
        # open cursor, define and run query, fetch results
        cursor = conn.cursor()
        table_name = "station_get_mes"
        column_name = staion_name
        if staion_name == 'id':
            sql=  sql = f"INSERT INTO {table_name} (id) VALUES ('{chat_id}')"
        else:
            # Preparing SQL query to INSERT a record into the database.
            sql = f"UPDATE {table_name} SET {column_name} = CURRENT_TIMESTAMP WHERE id = '{chat_id}'"
            # Executing the SQL command
        cursor.execute(sql)
            # Commit your changes in the database
        conn.commit()
             # close the cursor and database connection
        cursor.close()

        return True
    # catch exception and print error message
    except Error as err:
        print('db_update_del - Error message: ' + err.msg)
        return False



## insert new user to the users id
def insert_numbers(user_id, user_name, station_list, wind_to_alert_knots, wind_to_alert_max):
    try:
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='localhost', database='windbot_db'
        )
        cursor = conn.cursor()
        station_list_max = []
        for station in station_list:
            station = station+'_max'
            station_list_max.append(station)
        print(station_list_max)
        columns = ['id', 'first_name'] + station_list + station_list_max

        # Create a new row and insert user ID, name, and number into the relevant columns
        sql = f"INSERT INTO users ({', '.join(columns)}) VALUES ('{user_id}', '{user_name}',"
        for column in station_list:
            sql += f" {wind_to_alert_knots},"
        for column in station_list_max:
                sql += f" {wind_to_alert_max},"
                            # Remove the trailing comma and close the SQL statement
        sql = sql.rstrip(",") + ")"

        cursor.execute(sql)
        conn.commit()

        cursor.close()
        conn.close()
        print("User data inserted successfully.")
        return True
    except mysql.connector.Error as e:
        print("Error inserting user data:", e)
        return False

##delete user from the users table by id
def delete_row_by_id(user_id, table_name):
    try:
        # establishing the connection
        conn = mysql.connector.connect(
            user='root', password='Uri0524734764', host='127.0.0.1', database='windbot_db')
        # open cursor, define and run query, fetch results


        cursor = conn.cursor()

        # Delete the row based on the user ID
        sql = f"DELETE FROM {table_name} WHERE id = '{user_id}'"
        cursor.execute(sql)
        conn.commit()

        cursor.close()
        conn.close()
        print("Row deleted successfully.")
        return True
    except mysql.connector.Error as e:
        print("Error deleting row:", e)
        return False







