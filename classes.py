from tools import *
from os import listdir
import telebot

bot_token = "527000621:AAFw5L5fQ_anKOTkRCa03JC2YeRxNz4g1E8"
bot = telebot.TeleBot(token = bot_token)

class User(object):

    def __init__(self, m):
        self.id = m.from_user.id
        if str(self.id) + '.json' in listdir('./user_data'):
            self.__dict__ = load_json(self.id)
            self.username = self.__dict__['username']
        else: # new user
            self.username = m.from_user.first_name
            self.is_new_user = True
            self.checkin_data = {}
            self.latest_timestamp = None
            new_user = {
                str(self.id): {
                        'id': self.id,
                        'username': self.username,
                        'checkin_data': self.checkin_data,
                        'is_new_user': self.is_new_user,
                        'latest_timestamp': None
                }
            }
            save_json(self)

    def check_in_out(self, in_out):
        date_label = datetime.fromtimestamp(self.latest_timestamp).strftime('%Y%m%d')
        try:
            self.checkin_data[date_label][in_out] = self.latest_timestamp
        except KeyError:
            self.checkin_data[date_label] = {}
            self.checkin_data[date_label][in_out] = self.latest_timestamp
        self.last_action = 'Checked ' + in_out
        bot.send_message(self.id, 'Checked ' + in_out + ' successfully.')
        save_json(self)

    def summarise(self):
        message = 'A summary of your hours so far.\n'
        time_total_dt = datetime.utcfromtimestamp(0)
        for key in self.checkin_data:
            try:
                in_time_dt = datetime.fromtimestamp(self.checkin_data[key]["in"])
                in_time = in_time_dt.strftime('%d.%m.%Y %H:%M')
                out_time_dt = datetime.fromtimestamp(self.checkin_data[key]["out"])
                out_time = out_time_dt.strftime('%H:%M')
                if in_time > out_time:
                    message = 'Checkin on {} later than checkout'
                time_checked_in_dt = out_time_dt - in_time_dt
                time_total_dt += time_checked_in_dt
                hours_day = int(time_checked_in_dt.seconds/3600)
                minutes_day = int((time_checked_in_dt.seconds%3600)/60)
                message += '\n{} to {}: {:02d}:{:02d}'.format(in_time, out_time, hours_day, minutes_day)
            except KeyError: # incomplete data for date
                pass
        hours_total = time_total_dt.hour
        minutes_total = time_total_dt.minute
        message += '\n\nTotal: ' + str(hours_total) + ' hours ' + str(minutes_total) + ' minutes.'
        return message