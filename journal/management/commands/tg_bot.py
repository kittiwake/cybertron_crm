from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardButton,InlineKeyboardMarkup
from journal.models import Teacher
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Объявление переменной бота
# https://www.youtube.com/@it_everyday/videos - посмотреть

bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)


@bot.message_handler(commands=['start'])
def start(message: Message):
    # проверить id в базе переподов и родаков
    # если уже есть 
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Я преподаватель',callback_data='teacher')
    btn2 = InlineKeyboardButton('Я родитель',callback_data='student')
    markup.row(btn1, btn2)
    bot.send_message(chat_id=message.chat.id, 
                     text='Здравствуйте!',
                     reply_markup=markup)
    
@bot.callback_query_handler(func=lambda callback: True)
def on_click(callback):
    # print(callback)
    if callback.data == 'teacher':
        start_teacher(callback.message)

def start_teacher(message: Message):
    reg = True
    try:
        teacher = Teacher.objects.get(tg_id=message.chat.id)
        if teacher.user_id:
            bot.send_message(chat_id=message.chat.id, 
                            text=f'''Здравствуйте, {teacher.last_name} {teacher.first_name}. Вы зарегистрированы на сайте.
                                Если хотите сменить логин/пароль, введите команду /reset''')
            reg = False
        else:
            bot.send_message(chat_id=message.chat.id, 
                            text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Пройдите регистрацию')

    except ObjectDoesNotExist:
        
        # получить юзернейм, найти в базе
        try:
            teacher = Teacher.objects.get(tg_name=message.chat.username)
            teacher.tg_id = message.chat.id
            teacher.save()
            if teacher.user_id:
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Вы зарегистрированы на сайте. \
                                    Если хотите сменить логин/пароль, введите команду /reset')
                reg = False
            else:
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Пройдите регистрацию')
            
        except ObjectDoesNotExist:
            
            teachers = Teacher.objects.filter(tg_id__isnull=True).filter(last_name=message.chat.last_name)
            if len(teachers) == 1:
                teacher = teachers[0]
                del teachers
                teacher.tg_id = message.chat.id
                teacher.save()
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Пройдите регистрацию')
            else:
                reg = False
                bot.send_message(chat_id=message.chat.id, 
                                text='К сожалению, я не могу идентифицировать Вас по имени пользователя. Введите Вашу фамилию')
                bot.register_next_step_handler(message, check_name)
    if reg:
        # запрос логина и пароля
        bot.send_message(chat_id=message.chat.id, 
                        text=f'Для регистрации на сайти введите логин.')
        bot.register_next_step_handler(message, enter_login, teacher=teacher)

def check_name(message: Message):
    teacher = Teacher.objects.filter(tg_id__isnull=True).filter(last_name=message.text.capitalize())
    reg = False
    if not teacher:
        bot.reply_to(message=message, 
                     text='Я не нашел такой фамилии в списке преподавателей. Возможно, в наборе была допущена ошибка.\n\n\
Проверьте свой ввод и если нужно, повторите сначала. Если ошибок не было допущено, обратитесь к администратору')
    elif len(teacher) == 1:
        reg = True
        teacher[0].tg_id = message.chat.id
        teacher[0].tg_name = message.chat.username
        teacher[0].save()
        bot.send_message(chat_id=message.chat.id, 
                        text=f'Здравствуйте, {teacher[0].last_name} {teacher[0].first_name}. Пройдите регистрацию')
    else:
        bot.reply_to(message=message, 
                     text='''К сожалению, я не могу идентифицировать Вас по фамилии. Создайте имя пользователя в телеграм
и передайте его администратору.''')
    if reg:
        # запрос логина и пароля
        bot.send_message(chat_id=message.chat.id, 
                        text=f'Для регистрации в портале введите логин.')
        bot.register_next_step_handler(message, enter_login, teacher=teacher[0])

def enter_login(message: Message, teacher: Teacher):
    bot.send_message(chat_id=message.chat.id, 
                text=f'Введите пароль.')
    bot.register_next_step_handler(message, enter_password, teacher=teacher, login=message.text)

def enter_password(message: Message, teacher: Teacher, login: str):
    try:
        user = User.objects.create(username=login)
        user.set_password(message.text)
        user.save()
        teacher.user_id = user
        teacher.save()
        bot.send_message(chat_id=message.chat.id, 
                    text=f'Регистрация прошла успешно!')
    except Exception as e:
        bot.send_message(chat_id=message.chat.id, 
                    text=f'Ошибка регистрации: {e}')

@bot.message_handler(commands=['reset'])
def reset_registration(message: Message):
    teacher = Teacher.objects.get(tg_id=message.chat.id)
    print(teacher.values())


@bot.message_handler(commands=['info'])
def echo(message: Message):
    bot.send_message(chat_id=message.chat.id, text=message)
    # print(message.json)

# @bot.message_handler()
# def echo(message: Message):
#     bot.send_message(chat_id=message.chat.id, text=message.text)
    # print(message.json)
    # bot.reply_to(message=message, text="I'm glad to see you!")


# Название класса обязательно - "Command"
class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2) # Сохранение обработчиков
        bot.load_next_step_handlers()								# Загрузка обработчиков
        bot.infinity_polling()			