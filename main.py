import random
import sqlalchemy
import psycopg2
import os

from sqlalchemy import func, and_
from sql_models import create_tables, Words, Translations, Users, UserInfo
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

load_dotenv()
print('Start telegram bot...')
my_login = os.getenv('MY_LOGIN')
my_password = os.getenv('MY_PASSWORD')
my_location = os.getenv('MY_LOCATION')
my_port = os.getenv('MY_PORT')
my_db = os.getenv('MY_DB')
DSN = f'postgresql://{my_login}:{my_password}@{my_location}:{my_port}/{my_db}'
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

# session
Session = sessionmaker(bind=engine)
session = Session()

# storage
state_storage = StateMemoryStorage()
token_bot = os.getenv('MY_TOKEN')
bot = TeleBot(token_bot, state_storage=state_storage)

# known_users = []
# qu = session.query(UserInfo.telegram_id).all()
# if len(qu) > 0:
#     for r in qu:
#         known_users.append(r[0])
# print(known_users)
userStep = {}
qu = session.query(UserInfo.chat_id, UserInfo.user_step).all()
for row in qu:
    userStep[row[0]] = row[1]
print(userStep)
buttons = []


def insert_base_data(message):
    u1 = Users(login=message.from_user.username)

    w1 = Words(word='She', users=u1)
    w2 = Words(word='Green', users=u1)
    w3 = Words(word='White', users=u1)
    w4 = Words(word='He', users=u1)
    w5 = Words(word='Black', users=u1)
    w6 = Words(word='Bird', users=u1)
    w7 = Words(word='Cat', users=u1)
    w8 = Words(word='Dog', users=u1)
    w9 = Words(word='Snake', users=u1)
    w10 = Words(word='Camel', users=u1)

    t1 = Translations(trans='Она', words=w1)
    t2 = Translations(trans='Зеленый', words=w2)
    t3 = Translations(trans='Белый', words=w3)
    t4 = Translations(trans='Он', words=w4)
    t5 = Translations(trans='Черный', words=w5)
    t6 = Translations(trans='Птица', words=w6)
    t7 = Translations(trans='Кошка', words=w7)
    t8 = Translations(trans='Собака', words=w8)
    t9 = Translations(trans='Змея', words=w9)
    t10 = Translations(trans='Верблюд', words=w10)

    ui1 = UserInfo(first_name=message.from_user.first_name, last_name=message.from_user.last_name,
                   telegram_id=message.from_user.id, chat_id=message.chat.id, user_step='start', users=u1)
    session.add_all([u1, w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, ui1])
    session.commit()

    qu = session.query(UserInfo.chat_id, UserInfo.user_step).filter(UserInfo.chat_id==message.chat.id)
    userStep[qu[0]] = qu[1]


@bot.message_handler(commands=['start'])
def user_init(message):
    q = session.query(Users.login).all()
    if len(userStep) > 0:
        if message.from_user.id not in userStep:
            insert_base_data(message)
            get_user_step(message.from_user.id)

        start_state(message)
        bot.set_state(message.from_user.id, MyStates.start, message.chat.id)
        userStep[message.from_user.id] = 'translate'
        # create_cards(message)
        random_word_info = session.query(Users.login, Words.word, Words.id).join(Words).filter(
            Users.login == message.from_user.username).order_by(func.random()).first()
        target_word = random_word_info[1]
        translate = session.query(Words.word, Translations.trans).join(Translations).filter(
            Words.id == random_word_info[2])
        translate = translate[0][1]
        others_info = session.query(Users.login, Words.word, Words.id).join(Words).filter(and_(
            Users.login == message.from_user.username, Words.id != random_word_info[2])).order_by(
            func.random()).limit(4)
        others = []
        for row in others_info:
            others.append(row[1])
        get_user_step(message.from_user.id)
    else:
        start_state(message)
        insert_base_data(message)
        get_user_step(message.from_user.id)


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()
    start = State()
    translation = State()
    delete = State()
    done = State()
    new_word = State()
    new_trans = State()
    added = State()


def get_user_step(uid):
    if uid in userStep:
        print('Old user')
        return userStep[uid]
    else:
        # known_users.append(uid)
        userStep[uid] = 'start'
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(state=MyStates.translation)
def create_cards(message):
    cid = message.chat.id
    if cid not in userStep:
        # known_users.append(cid)
        userStep[cid] = 'start'
        start_state(message)
        bot.set_state(message.from_user.id, MyStates.start, message.chat.id)
        user_init(message)
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []

    random_word_info = session.query(Users.login, Words.word, Words.id).join(Words).filter(
        Users.login == message.from_user.username).order_by(func.random()).first()
    target_word = random_word_info[1]

    translate = session.query(Words.word, Translations.trans).join(Translations).filter(Words.id == random_word_info[2])
    translate = translate[0][1]
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others_info = session.query(Users.login, Words.word, Words.id).join(Words).filter(and_(
        Users.login == message.from_user.username, Words.id != random_word_info[2])).order_by(func.random()).limit(4)
    others = []
    for row in others_info:
        others.append(row[1])
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    userStep[message.from_user.id] = 'translate'

    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    bot.set_state(message.from_user.id, MyStates.delete, message.chat.id)
    bot.send_message(message.chat.id, "Введите слово, которое вы хотите удалить:")


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    print(cid)
    userStep[cid] = 'add'
    print(userStep)
    bot.set_state(message.from_user.id, MyStates.new_word, message.chat.id)
    bot.send_message(message.chat.id, "Введите на английском слово, которое вы хотите добавить:")


def start_state(message):
    bot.send_message(message.chat.id, "Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить "
                                      "в удобном для себя темпе."
                                      "У тебя есть возможность использовать тренажёр, как конструктор, "
                                      "и собирать свою собственную базу для обучения. Для этого воспрользуйся инструментами:"
                                      "добавить слово ➕,удалить слово 🔙.Ну что, начнём ⬇️")
    # next_cards(message)


@bot.message_handler(state=MyStates.new_word)
def add_word(message):
    bot.send_message(message.chat.id, "Введите перевод слова, которое вы хотите добавить:")
    bot.set_state(message.from_user.id, MyStates.new_trans, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['new_word'] = message.text


@bot.message_handler(state=MyStates.new_trans)
def add_trans(message):
    bot.set_state(message.from_user.id, MyStates.added, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['new_trans'] = message.text
        print(data)
        qu = session.query(Users.id, UserInfo.telegram_id).join(UserInfo).filter(
            UserInfo.telegram_id == message.from_user.id)
        for row in qu:
            print(row)
        w1 = Words(word=data['new_word'], user_id=row[0])
        t1 = Translations(trans=data['new_trans'], words=w1)
        session.add_all([w1, t1])
        session.commit()
    count = session.query(func.count(Words.id)).filter(Words.user_id == row[0])
    bot.send_message(message.chat.id, f'Вы изучаете {count[0][0]} слов')
    create_cards(message)


@bot.message_handler(state=MyStates.delete)
def delete_word(message):
    print('deletion in progress')
    text = message.text
    print(text)
    q = session.query(Users.id, UserInfo.telegram_id).join(UserInfo).filter(
        UserInfo.telegram_id == message.from_user.id)
    for r in q:
        user = r[0]
    qu = session.query(Words.word, Translations.trans, Translations.word_id).join(Translations).filter(
        Words.user_id == user).all()
    word_in_voc = False
    for row in qu:
        # print(row)
        if text == row[0] or text == row[1]:
            word_in_voc = True
            print(row)
            session.query(Translations).filter(Translations.trans == row[1]).filter(
                Translations.word_id == row[2]).delete(synchronize_session='fetch')
            session.commit()
            session.query(Words).filter(Words.word == row[0]).filter(Words.user_id == user).delete(
                synchronize_session='fetch')
            session.commit()
    if word_in_voc:
        bot.send_message(message.chat.id, f'Слово {text} удалено.')
    else:
        bot.send_message(message.chat.id, 'Вы не изучаете такое слово.')
    create_cards(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    chat_id = message.chat.id
    user_state = get_user_step(chat_id)

    if user_state == 'translate':
        text = message.text
        markup = types.ReplyKeyboardMarkup(row_width=2)
        hint = ''
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['target_word']
            if text == target_word:
                hint = show_target(data)
                hint_text = ["Отлично!❤", hint]
                # next_btn = types.KeyboardButton(Command.NEXT)
                # add_word_btn = types.KeyboardButton(Command.ADD_WORD)
                # delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
                # buttons.extend([next_btn, add_word_btn, delete_word_btn])
                hint = show_hint(*hint_text)
            else:
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                hint = show_hint("Допущена ошибка!",
                                 f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
        markup.add(*buttons)
        bot.send_message(message.chat.id, hint, reply_markup=markup)

    elif user_state == 'start':
        pass

    else:
        print('Unknown state')


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)

session.close()
