# hours

A means of keeping track of hours using a checkin/checkout system, e.g. for shifts at work. 

## Getting started

Type the following into your terminal (Linux):

```
pip install pyTelegramBotAPI
git clone https://github.com/ollieacappella/hours
cd hours
mkdir user_data
```

You will also need to create a Telegram bot ([instructions here](https://www.sohamkamani.com/blog/2016/09/21/making-a-telegram-bot/)) and save its API token into the file `hours/bot_token` as raw text.

Then, run with

```
python3 hours.py
```

## Using the bot

Communicate with your bot via Telegram. Initialise your own data with `/start`. To change the name it has saved for you, use `/newname`. 

To check in or out, use `/in` or `out`, respectively.

To see a summary of the hours you have saved, use `/summary`. 

To see a list of all available commands and their functions, use `/help` or `/info`. 