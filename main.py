import telebot
from telebot import types
from datetime import datetime
import re
import requests
import os

API_TOKEN = 'TOKEN'
PATH_FOR_DOWNLOAD = 'docs/'
# REGEXP_FOR_FULLNAME = r'^([А-Я][а-я]*)(\s[А-Я][а-я]*)(\s[А-Я][а-я]*)?([\s\-][А-Я][а-я]*)?$'
# REGEXP_FOR_EMAIL = r'^[a-zA-Z]+@[a-zA-z]+\.[a-zA-Z]+$'
# REGEXP_FOR_PHONE = r'^(\+7|8)[\s\-]?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})'

PREFERENCE_AGE = 8

bot = telebot.TeleBot(API_TOKEN)

markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
itembtn1 = types.KeyboardButton('Зарегестрироваться')
itembtn3 = types.KeyboardButton('Помошь(не работает)')
markup.add(itembtn1, itembtn3)

user_dict = {}
kvantums = {'Промробо', 'VR/AR', 'Хайтек', "Био", "Промдизайн", "IT"}
formats_msg = '(*.docx, *.odf, *.pdf, *.jpg, *.png)'
stop_msg = 'Если хотите прервать регистрацию, введите /stop'


class User:
    def __init__(self, name):
        self.name = name
        self.birth = None
        self.sex = None
        self.kvantum = None
        self.phone = None
        self.parantphone = None
        self.parantname = None
        self.email = None
        self.shift = None
        self.enrollment = None
        self.consent = None
        self.certificate = None
        self.snils = None
        self.parantpass = None
        self.passport = None


def get_file_id(message):
    file_id = None
    if message.text is not None:
        raise Exception('Это что текст? Ты серьёзно?')
    if message.document is not None:
        print(message.document.mime_type)
        file_id = message.document.file_id
    if message.photo is not None:
        file_id = message.photo[0].file_id
    return file_id


def download_and_write_to_file(file_id):
    if not os.path.exists(PATH_FOR_DOWNLOAD):
        os.makedirs(PATH_FOR_DOWNLOAD)
    file_info = bot.get_file(file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    open(PATH_FOR_DOWNLOAD + str(file_id), "wb").write(file.content)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет, выбери действие", reply_markup=markup)


@bot.message_handler(commands=['help'])
def send_help(message):
    pass


@bot.message_handler(commands=['stop'])
def stop(message):
    print('stop')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.send_message(message.chat.id, 'Ну не хочешь, так не хотчешь твоё дело', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "зарегестрироваться":
        msg = bot.reply_to(message, "Что бы начать регистрацию введите ваше ФИО. " + stop_msg)
        bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        name = message.text
        if name is None:
            raise Exception("Пришли слово")
#         if not re.fullmatch(REGEXP_FOR_FULLNAME, name):
#             raise Exception("Вы ввели неправильный формат имени")
        user = User(name)
        user_dict[chat_id] = user
        user.name = name
        msg = bot.reply_to(message, 'Введите ваш год рождения dd.mm.yyyy. ' + stop_msg)

        bot.register_next_step_handler(msg, process_birth_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_name_step)


def process_birth_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        birth = message.text
        if birth is None:
            raise Exception("Пришли слово")
#         birth_date = datetime.strptime(birth, "%d.%m.%Y")
#         now_date = datetime.today()
#         user_year = int((now_date - birth_date).days / 365)
#         if user_year < PREFERENCE_AGE:
#             bot.clear_step_handler_by_chat_id(message.chat.id)
#             bot.send_message(message.chat.id, 'Возвращайся, когда подрастешь, салага', reply_markup=markup)
#             return
        user = user_dict[chat_id]
        user.birth = birth
        markup1 = types.ReplyKeyboardMarkup()
        markup1.add('мужской', 'женский')
        msg = bot.reply_to(message, 'Какой твой пол? ' + stop_msg, reply_markup=markup1)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_birth_step)


def process_sex_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        sex = message.text
        if sex is None:
            raise Exception("Пришли слово")
        print(sex)
        user = user_dict[chat_id]
        if (sex.lower() == 'мужской') or (sex.lower() == 'женский'):
            user.sex = sex
        else:
            print('Почему то не равны')
            raise Exception("Да что не так")
        print('сравнил')

        markup2 = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
        for k in kvantums:
            markup2.add(k)
        msg = bot.reply_to(message, 'Какой квантум хочешь? ' + stop_msg, reply_markup=markup2)
        bot.register_next_step_handler(msg, process_kvantum_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_sex_step)


def process_kvantum_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        kvantum = message.text
        if kvantum is None:
            raise Exception("Пришли слово")

        if kvantum in kvantums:
            user.kvantum = kvantum
        else:
            raise Exception()
        msg = bot.reply_to(message, 'Какой email у тебя? ' + stop_msg)
        bot.register_next_step_handler(msg, process_email_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_kvantum_step)


def process_email_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        email = message.text
        if email is None:
            raise Exception("Пришли слово")
#         if not re.fullmatch(REGEXP_FOR_EMAIL, email):
#             raise Exception("Вы ввели неправильный email")
        user.email = email
        markup3 = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup3.add("В первую", "Во вторую")
        msg = bot.reply_to(message, "В какую смену ходить хочешь? " + stop_msg, reply_markup=markup3)
        bot.register_next_step_handler(msg, process_shift_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_email_step)


def process_shift_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        shift = message.text
        if shift is None:
            raise Exception("Пришли слово")
        user.shift = shift
        msg = bot.reply_to(message, "Введите ФИО одного родителя" + stop_msg)
        bot.register_next_step_handler(msg, process_parantname_step)
    except Exception as e:
        markup3 = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup3.add("В первую", "Во вторую")
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный?', reply_markup=markup3)
        bot.register_next_step_handler(msg, process_shift_step)


def process_parantname_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        parantname = message.text
        if parantname is None:
            raise Exception("Пришли слово")
#         if not re.fullmatch(REGEXP_FOR_FULLNAME, parantname):
#             raise Exception("Введите праивльные вормат ФИО")

        user.parantname = parantname
        msg = bot.reply_to(message, 'Введите свой телефон. ' + stop_msg)

        bot.register_next_step_handler(msg, process_phone_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_parantname_step)


def process_phone_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        phone = message.text
        if phone is None:
            raise Exception("Пришли текст")
#         if not re.fullmatch(REGEXP_FOR_PHONE, phone):
#             raise Exception("Не правильный номер телефона")

        user.phone = phone
        msg = bot.reply_to(message, 'Введите телефон родителя. ' + stop_msg)

        bot.register_next_step_handler(msg, process_parantphone_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_phone_step)


def process_parantphone_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        parantphone = message.text
        if parantphone is None:
            raise Exception("Пришли слово")
#         if not re.fullmatch(REGEXP_FOR_PHONE, parantphone):
#             raise Exception("Не правильный телефон")

        user.parantphone = parantphone
        msg = bot.reply_to(message, 'Кинь заявление на зачисление ' + formats_msg + '. ' + stop_msg)

        bot.register_next_step_handler(msg, process_enrollment_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_parantphone_step)


def process_enrollment_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        print(message.document)
        print(message.photo)
        id_file = get_file_id(message)
        download_and_write_to_file(id_file)
        user.enrollment = id_file
        msg = bot.reply_to(message, 'Кинь согласие на обработку данных ' + formats_msg + '. ' + stop_msg)

        bot.register_next_step_handler(msg, process_consent_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_enrollment_step)


def process_consent_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        id_file = get_file_id(message)
        download_and_write_to_file(id_file)
        user.consent = id_file
        msg = bot.reply_to(message, 'Кинь свидетельство о рождении ' + formats_msg + '. ' + stop_msg)

        bot.register_next_step_handler(msg, process_certificate_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_consent_step)


def process_certificate_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        id_file = get_file_id(message)
        download_and_write_to_file(id_file)
        user.certificate = id_file
        msg = bot.reply_to(message, 'Кинь СНИЛС ' + formats_msg + '. ' + stop_msg)

        bot.register_next_step_handler(msg, process_snils_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_certificate_step)


def process_snils_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        id_file = get_file_id(message)
        download_and_write_to_file(id_file)
        user.snils = id_file
        msg = bot.reply_to(message, 'Кинь паспорт родителя ' + formats_msg + '. ' + stop_msg)

        bot.register_next_step_handler(msg, process_parantpass_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_snils_step)


def process_parantpass_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        id_file = get_file_id(message)
        download_and_write_to_file(id_file)
        user.parantpass = id_file
        msg = bot.reply_to(message, 'Кинь паспорт ребенка ' + formats_msg + '. ' + stop_msg)

        bot.register_next_step_handler(msg, process_passport_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_parantpass_step)


def process_passport_step(message):
    if message.text == '/stop':
        stop(message)
        return
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        id_file = get_file_id(message)
        download_and_write_to_file(id_file)
        user.passport = id_file

        markup4 = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup4.add("Я согласен на обработку данных")
        markup4.add("Я не согласен на обработку данных")
        msg = bot.reply_to(message, 'Ваша заявка подана ' + user.name +
                           '\n\n Ваш возвраст: ' + str(user.birth) +
                           '\n\n Пол: ' + user.sex +
                           '\n\n Квантум: ' + user.kvantum +
                           '\n\n email: ' + user.email +
                           '\n\n Заявление на зачисление: ' + "true" +
                           '\n\n Согласие на обработку персональных данных: ' + "true" +
                           '\n\n Свидетельсво о рождении: ' + "true" +
                           '\n\n СНИЛС: ' + "true" +
                           '\n\n Паспорт родителя: ' + 'true' +
                           '\n\n Паспорт ребенка: ' + "true", reply_markup=markup4)
        bot.register_next_step_handler(msg, process_last_step)
    except Exception as e:
        msg = bot.reply_to(message, 'oooops. Думаешь самый умный? ' + str(e.args[0]))
        bot.register_next_step_handler(msg, process_passport_step)


def process_last_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        print('Кол-во пользователей: ' + str(len(user_dict)))
        if message.text == 'Я не согласен на обработку данных':
            user_dict.pop(chat_id)
            print('Кол-во пользователей: ' + str(len(user_dict)))
            bot.send_message(chat_id, 'Извините, но нам такие не нужны')
        else:
            bot.send_message(chat_id, 'Раз вы согласны на обработку персональных данных, тогда мы рассмотрим вашу '
                                      'заявку')
    except Exception as e:
        pass


@bot.message_handler(content_types=['document'])
def get_document(message):
    print(message.document.mime_type)
    print(message.text)
    download_and_write_to_file(message.document.file_id)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    print(message.text)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.polling()
