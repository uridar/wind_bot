
# Windbot

Windbot is a Python project that utilizes the Telebot library to create a Telegram bot for wind alerts. The bot fetches real-time wind data from the Windguru website and sends alerts to users based on their specified wind speed thresholds.

## Prerequisites

To run this script, you need to have the following:

- Python 3 installed on your machine
- The necessary Python packages installed (`re`, `mysql.connector`, `datetime`, `requests`, `bs4`, `time`, `db_library`, `telebot`)
- MySQL database with the appropriate tables created 

## Setup

1. Clone or download the repository to your local machine.
2. Install the required Python packages using `pip` or your preferred package manager.
3. Open `password_holder.py` file and replace `mysql` with your mysql server password.
4. replace wind_bot_tokenwind_bot_token  with your Telegram Bot token .
5. Update the MySQL connection details and database name in the `db_library.py` file.
6. Run the `telebot_2.0.py` script to start the Telegram bot.
7. run the wind_script_20.py script to featch the wind data and send to the users.
8. Interact with the bot on Telegram to receive wind alerts.

## Usage

1. Start a chat with the Windbot on Telegram.
2. The bot will automatically fetch real-time wind data from Windguru.
3. Users can register to receive wind alerts by specifying their desired wind speed thresholds.
4. Users can select specific weather stations to receive updates from.
5. Wind alerts will be sent to registered users based on their preferences.

## Additional Information

### Code Snippet 1

The first code snippet (`telebot_2.0.py`) is responsible for handling user registration, fetching wind data from Windguru, and sending alerts to registered users. It uses the `telebot` library for Telegram bot functionality.

### Code Snippet 2

The second code snippet (`db_library.py`) provides database-related functions for fetching, updating, and deleting data from the MySQL database used by the Windbot. It interacts with the database using the `mysql.connector` package.


### Code Snippet 3
the theard code snippet ('wind_script20.py') featch the wind data from windguru and send it to the users.

## Contributors

This script was developed by uri dar. Feel free to contribute and make improvements!

Please note that this readme file is a template and should be customized according to your specific project requirements.
