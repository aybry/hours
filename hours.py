import telebot
import json
import re
import time
import logging
from telebot import types
from tools import *
from classes import *
from datetime import datetime

with open('bot_token', 'r') as f:
    bot_token = f.read()
bot = telebot.TeleBot(token = bot_token)
logger = telebot.logger
# logger.setLevel(logging.DEBUG)

commands = {
    'start'     : 'Welcome message and user initialisation',
    'newname'   : 'Change name',
    'in'        : 'Check in',
    'out'       : 'Check out',
    'summary'   : 'See summary of hours in database',
    'active'    : 'Check if bot is online'
    'info'      : 'Lists available commands and their function',
    'help'      : 'Lists available commands and their function'
}

@bot.message_handler(commands=['help', 'info'])
def cmd_help(m):
    user = User(m)
    help_text = "The following commands are available: \n\n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(user.id, help_text) # send the generated help page

@bot.message_handler(commands = ['test'])
def testing(m):
    print("This command is out of action.")

@bot.message_handler(commands = ['active'])
def change_username(m):
    user = User(m)
    m = bot.send_message(user.id, 'Still alive and kicking!')

@bot.message_handler(commands = ['start'])
def begin(m):
    user = User(m)
    if not user.is_new_user:
        bot.send_message(user.id, 'You\'re already initialised as ' 
                                 + user.username
                                 + '. '
                                 + 'Select another command.')
    else:
        m = bot.send_message(user.id, 'Hello new user!' 
                                    + '\n\nIs your name ' 
                                    + user.username 
                                    + '?', 
                             reply_markup=yes_no_buttons())
        bot.register_next_step_handler(m, process_name_answer)
    
@bot.message_handler(commands = ['newname'])
def change_username(m):
    user = User(m)
    m = bot.send_message(user.id, 'So what is your name?')
    bot.register_next_step_handler(m, process_name_step)

def process_name_answer(m):
    user = User(m)
    if m.text.lower() in ['yes', 'y', 'ja']:
        bot.send_message(user.id, 'Saved name as ' 
                                + user.username)
        user.is_new_user = False
        save_json(user)
    elif m.text.lower() in ['no', 'n', 'nein']:
        new_name_message = bot.send_message(user.id, 'So what is your name?')
        bot.register_next_step_handler(new_name_message, process_name_step)
    else:
        bot.send_message(user.id, 'Response not recognised. Action cancelled.')

def process_name_step(m):
    user = User(m)
    user.username = m.text
    user.is_new_user = False
    user.last_action = 'Changed name'
    save_json(user)
    bot.send_message(user.id, 'Saved new name as ' + user.username)

@bot.message_handler(commands = ['in', 'out'])
def cmd_check_in_out(m):
    user = User(m)
    in_out = m.text[1:]
    current_datetime = datetime.now()
    current_timestamp = time.mktime(current_datetime.timetuple())
    user.latest_timestamp = int(current_timestamp)
    user.last_action = 'Checking ' + in_out
    save_json(user)
    bot.send_message(user.id, 'You are checking ' + in_out 
                            + ' on ' + current_datetime.strftime('%d.%m.%Y') 
                            + ' at ' + current_datetime.strftime('%H:%M') 
                            + '. Is this correct?', 
                     reply_markup=yes_no_buttons())
    bot.register_next_step_handler(m, process_check_answer)

def process_check_answer(m):
    user = User(m)
    in_out = user.last_action.split()[-1]
    time_int = user.latest_timestamp
    date_label = datetime.fromtimestamp(user.latest_timestamp).strftime('%Y%m%d')
    if m.text.lower() == 'cancel':
        bot.send_message(user.id, 'Cancelled.')
        return
    elif m.text.lower() == 'yes':
        try:
            if in_out in user.checkin_data[date_label].keys():
                time_saved_ts = user.checkin_data[date_label][in_out]
                time_saved = datetime.fromtimestamp(time_saved_ts).strftime('%Y.%m.%d %H:%M')
                confirm_overwrite = bot.send_message(user.id, 'Check' 
                                                    + in_out 
                                                    + ' data already exists for this date ('
                                                    + time_saved
                                                    + '). Overwrite?')
                bot.register_next_step_handler(confirm_overwrite, process_overwrite_step)
            else: 
                user.check_in_out(in_out)
        except KeyError:
            user.check_in_out(in_out)
    elif m.text.lower() == 'no':
        new_name_message = bot.send_message(user.id, 'At what time do you want to check ' 
                                                    + in_out 
                                                    + '? (Format: hhmm) Or type \'cancel\' to cancel.')
        bot.register_next_step_handler(new_name_message, process_time_step)
    else:
        bot.send_message(user.id, 'Response not recognised. Action cancelled.')

def process_time_step(m):
    user = User(m)
    time_formats = ['%H%M', '%H:%M', '%H.%M']
    if m.text.lower() == 'cancel':
        bot.send_message(user.id, 'Cancelled.')
        return
    for time_format in time_formats:
        try:
            date_today_str = datetime.today().strftime('%Y%m%d')
            custom_time_datetime = datetime.strptime(date_today_str + m.text,
                                                '%Y%m%d' + time_format)
            custom_time = custom_time_datetime.timestamp()
            in_out = user.last_action.split()[-1]
            user.latest_timestamp = int(custom_time)
            save_json(user)
            user.check_in_out(in_out)
            break
        except ValueError:
            pass
            
def process_overwrite_step(m):
    user = User(m)
    in_out = user.last_action.split()[-1]
    if m.text.lower() == 'cancel':
        bot.send_message(user.id, 'Cancelled.')
        return
    elif m.text.lower() == 'yes':
        user.check_in_out(in_out)
    elif m.text.lower() == 'no':
        bot.send_message(user.id, 'Data was not changed.')
    else:
        bot.send_message(user.id, 'Response not recognised. Action cancelled.')

@bot.message_handler(commands = ['summary'])
def cmd_summary(m):
    user = User(m)
    message = user.summarise()
    bot.send_message(user.id, message)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=1)

# # Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# # WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.set_update_listener(listener)

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            logger.error(ex)
            time.sleep(10)
        except:
            logger.error('Some other error')
            time.sleep(10)