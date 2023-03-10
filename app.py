import telebot
import requests
from telebot import types
import json

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

# r = requests.get(f'https://www.nbrb.by/api/exrates/rates/{selected_currency}?parammode=2')
#     total_base = json.loads(r.content)

global users_by_chat_id
users_by_chat_id = dict()


@bot.message_handler(commands=['start', 'help'])
def help_url(message):
    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton(text='YES', callback_data='yes')
    btn_no = types.InlineKeyboardButton(text='NO', callback_data='no')
    markup.add(btn_yes, btn_no)
    bot.send_message(message.from_user.id, f" <b>Привет \U0001F603! \n</b>"
                                           f"Приложение поможет Вам определить стоимость валюты для покупки. Начнем? ",
                     reply_markup=markup, parse_mode="html")


@bot.callback_query_handler(func=lambda call: call.data == 'no')
def callback_worker(call):
    markup = types.InlineKeyboardMarkup()
    btn_url = types.InlineKeyboardButton(text='Перейти на сайт НБРБ',
                                         url='https://www.nbrb.by/statistics/rates/ratesdaily.asp')
    markup.add(btn_url)
    bot.send_message(call.from_user.id, "По ссылке ниже можно просмотреть официальный курс валют Нац Банка РБ",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def help_url(message):
    markup = types.InlineKeyboardMarkup()
    btn_usd = types.InlineKeyboardButton(text='USD', callback_data='USD')
    btn_eur = types.InlineKeyboardButton(text='EUR', callback_data='EUR')
    btn_rub = types.InlineKeyboardButton(text='RUB', callback_data='RUB')
    markup.add(btn_usd, btn_eur, btn_rub)
    bot.send_message(message.from_user.id, " Какой тип валюты Вас интересует?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    users_by_chat_id[call.message.chat.id] = call.data
    message = 'Сколько ' + call.data + ' Вы хотите купить?'
    bot.send_message(call.message.chat.id, message)


# расчет
@bot.message_handler(content_types=['text'])
def receive_text(message):
    r = requests.get(f'https://www.nbrb.by/api/exrates/rates/{users_by_chat_id[message.from_user.id]}?parammode=2')
    total_base = json.loads(r.content)
    cur_officialrate = total_base["Cur_OfficialRate"]
    cur_scale = total_base["Cur_Scale"]
    try:
        summa = round(abs(float(message.text))*total_base["Cur_OfficialRate"]/total_base["Cur_Scale"], 2)
        bot.send_message(message.from_user.id, f"Текущий курс за {cur_scale} {users_by_chat_id[message.from_user.id]} "
                                               "= " f"{cur_officialrate}p.\n <b>Вам необходимо: " + str(summa) +
                         " p.</b>", parse_mode="html")
    except ValueError:
        bot.send_message(message.from_user.id, f"Вы ввели некорректное значение\U0001F648  Попробуйте еще раз!")


bot.polling(none_stop=True, interval=0)
