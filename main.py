import telebot
import json
import os
import random
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7487367613:AAGZVFdqiY6fkOecoKVY_12NW_N0Abq8S_Q'
bot = telebot.TeleBot(API_TOKEN)

user_symbols = {}
user_languages = {}
in_game_users = {}
user_stats = {}

def load_translation(language):
    with open(f'language/{language}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_symbols():
    with open('symbols.json', 'r', encoding='utf-8') as f:
        return json.load(f)



symbols = load_symbols()

@bot.message_handler(func=lambda message: message.text in [
    load_translation(user_languages.get(message.from_user.id, 'en'))['very_easy'],
    load_translation(user_languages.get(message.from_user.id, 'en'))['easy'],
    load_translation(user_languages.get(message.from_user.id, 'en'))['medium'],
    load_translation(user_languages.get(message.from_user.id, 'en'))['hard'],
    load_translation(user_languages.get(message.from_user.id, 'en'))['very_hard'],
])
def show_symbols(message):
    user_id = message.from_user.id

    if user_id not in user_languages:
        user_languages[user_id] = 'en'

    lang = user_languages[user_id]
    translations = load_translation(lang)

    difficulty = message.text
    if difficulty == translations['very_easy']:
        symbol_count = 2
    if difficulty == translations['easy']:
        symbol_count = 3
    if difficulty == translations['medium']:
        symbol_count = 5
    if difficulty == translations['hard']:
        symbol_count = 6
    if difficulty == translations['very_hard']:
        symbol_count = 7

    countdown_messages = ["Start game: 3", "Start game: 2", "Start game: 1"]


    for msg in countdown_messages:
        bot.send_message(message.chat.id, msg)
        time.sleep(1)

    random_symbols = random.sample(symbols['Symbols'], symbol_count)

    user_symbols[user_id] = random_symbols

    last_message_id = None

    for symbol in random_symbols:
        sent_message = bot.send_message(message.chat.id, symbol)

        if last_message_id:
            bot.delete_message(message.chat.id, last_message_id)

        last_message_id = sent_message.message_id

        time.sleep(1)

    bot.delete_message(message.chat.id, last_message_id)

@bot.message_handler(func=lambda message: message.from_user.id in user_symbols)
def check_symbols(message):
    user_id = message.from_user.id
    input_symbols = message.text.split()

    lang = user_languages[user_id]
    translations = load_translation(lang)

    if input_symbols == user_symbols[user_id]:
        bot.send_message(message.chat.id, translations["great"])
    else:
        bot.send_message(message.chat.id,translations["wrong"])


    del user_symbols[user_id]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('Русский🏳️'),
               telebot.types.KeyboardButton('English🇬🇧'),
               telebot.types.KeyboardButton('Українська🇺🇦'))
    user_languages[message.from_user.id] = 'en'
    bot.send_message(
        message.chat.id,
        """Hello! 
This bot will help train your memory with easy tasks to remember numbers and symbols.
To start the game and select difficulty, write /game.
But first, choose a language.""", reply_markup=markup



    )


@bot.message_handler(func=lambda message: message.text in ['Русский🏳️', 'English🇬🇧', 'Українська🇺🇦'])
def set_language(message):
    if message.text == 'Русский🏳️':
        user_languages[message.from_user.id] = 'ru'
    elif message.text == 'English🇬🇧':
        user_languages[message.from_user.id] = 'en'
    elif message.text == 'Українська🇺🇦':
        user_languages[message.from_user.id] = 'ua'

    lang = user_languages[message.from_user.id]
    translations = load_translation(lang)

    bot.send_message(message.chat.id, translations['start'], reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['language'])
def choose_language(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('Русский🏳️'),
               telebot.types.KeyboardButton('English🇬🇧'),
               telebot.types.KeyboardButton('Українська🇺🇦'))

    bot.send_message(message.chat.id, "Choose your language / Выберите язык / Оберіть мову", reply_markup=markup)


#markup = ReplyKeyboardMarkup(resize_keyboard=True)
#item1 = KeyboardButton("/start 🔄")
#item2 = KeyboardButton("/language 🗣️")
#item3 = KeyboardButton("/game 🎮")
#markup.add(item1, item2)
#markup.add(item3)

@bot.message_handler(commands=['game'])
def choose_difficult(message):
    user_id = message.from_user.id


    if user_id not in user_languages:

        user_languages[user_id] = 'en'


    lang = user_languages[user_id]
    translations = load_translation(lang)


    difficulty_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    difficulty_markup.add(
        telebot.types.KeyboardButton(translations['very_easy']),
        telebot.types.KeyboardButton(translations['easy']),
        telebot.types.KeyboardButton(translations['medium']),
        telebot.types.KeyboardButton(translations['hard']),
        telebot.types.KeyboardButton(translations['very_hard'])
    )


    bot.send_message(message.chat.id, translations['difficult'], reply_markup=difficulty_markup)

    def update_user_stats(user_id, level):

        if user_id not in user_stats:
            user_stats[user_id] = {
                'very_easy': 0,
                'easy': 0,
                'points': 0
            }


        if level == 'very_easy':
            user_stats[user_id]['very_easy'] += 1
            user_stats[user_id]['points'] += 1
        elif level == 'easy':
            user_stats[user_id]['easy'] += 1
            user_stats[user_id]['points'] += 2


    @bot.message_handler(func=lambda message: message.text == "Уровень Very Easy пройден")
    def handle_very_easy(message):
        user_id = message.from_user.id


        update_user_stats(user_id, 'very_easy')


        bot.send_message(message.chat.id, "Поздравляем! Вы прошли уровень 'Very Easy'. Вам начислен 1 балл.")

    @bot.message_handler(func=lambda message: message.text == "Уровень Easy пройден")
    def handle_easy(message):
        user_id = message.from_user.id


        update_user_stats(user_id, 'easy')


        bot.send_message(message.chat.id, "Поздравляем! Вы прошли уровень 'Easy'. Вам начислено 2 балла.")


    @bot.message_handler(commands=['stats'])
    def show_stats(message):
        user_id = message.from_user.id


        if user_id not in user_stats:
            bot.send_message(message.chat.id, "У вас пока нет статистики.")
            return

        # Извлекаем статистику пользователя
        stats = user_stats[user_id]
        very_easy_count = stats['very_easy']
        easy_count = stats['easy']
        points = stats['points']

        # Формируем сообщение со статистикой
        stats_message = (f"Ваша статистика:\n"
                         f"Уровень 'Very Easy' пройден: {very_easy_count} раз\n"
                         f"Уровень 'Easy' пройден: {easy_count} раз\n"
                         f"Всего баллов: {points}")

        # Отправляем сообщение со статистикой
        bot.send_message(message.chat.id, stats_message)
    
bot.polling()
