import numpy as np
from datetime import datetime, timedelta
import locale
from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import TeleBot
import re
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from journal.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


# Объявление переменной бота
# https://www.youtube.com/@it_everyday/videos - посмотреть

bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)
reg = False

@bot.message_handler(commands=['start'])
def start(message: Message):
    # проверить id в базе переподов и родаков
    # если уже есть 
    if message.chat.type == 'private':
        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton('Я преподаватель',callback_data='teacher')
        btn2 = InlineKeyboardButton('Я родитель',callback_data='student')
        markup.row(btn1, btn2)
        bot.send_message(chat_id=message.chat.id, 
                        text='Здравствуйте!',
                        reply_markup=markup)
    elif message.chat.type == 'group':
        # определить id группы
        id = message.chat.id
        tt = Timetable.objects.filter(tg_id=id)
        # если в базе нет, то спросить какой предмет (может несколько), какой препод и филиал
        # иначе просто список возможностей
        if tt:
            text = "Привет!"
            print(text)
        else:
            courses = Course.objects.filter(is_active=True)
            # + не имеет значения
            btns = []
            markup = InlineKeyboardMarkup()
            for c in courses:
                btns.append(InlineKeyboardButton(c.title,
                                                 callback_data=f'course={c.pk}'))
            btns.append(InlineKeyboardButton('Не имеет значения',
                                                 callback_data=f'course=-1'))
            for i in range(len(btns)//3):
                markup.row(btns[i*3], btns[i*3+1], btns[i*3+2])

            if (len(btns) - (i+1)*3) == 1:
                markup.row(btns[-1])
            elif (len(btns) - i*3) == 2:
                markup.row(btns[-2], btns[-1])

            bot.send_message(chat_id=message.chat.id, 
                            text='Какой курс?',
                            reply_markup=markup)


@bot.message_handler(commands=['poll'])
def start(message: Message):
    if message.chat.type == 'group':
        # номер группы
        # найти все пункты расписания из этой группы
        week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС','ПН', 'ВТ', 'СР']
        wd = datetime.today().weekday()
        sweek = week[wd:wd+3]
        tts = Timetable.objects.filter(tg_id=message.chat.id, active=True, day_of_week__in=sweek)
        if not tts:
            bot.send_message(chat_id=message.chat.id, 
                            text="Не могу определить расписание")
        else:
            tt_db = [[], [], [], [], []]
            for tt in tts:
                tt_db[0].append(tt.pk)
                tt_db[1].append(tt.timetb) 
                tt_db[2].append(tt.day_of_week)
                tt_db[3].append(tt.id_course)
                tt_db[4].append(datetime.today() + timedelta(week.index(tt.day_of_week) - datetime.today().weekday()))


            # сформировать вопрос: дата - предмет
            opt = []
            text = []
            if all(t==tt_db[3][0] for t in tt_db[3]):
                text.append(tt_db[3][0].title)
            else:
                opt.append([t.title for t in tt_db[3]])

            if all(t==tt_db[2][0] for t in tt_db[2]):
                text.append(tt_db[4][0].strftime('%d.%m'))
            else:
                text.append(min(tt_db[4]).strftime('%d.%m') + '-' + max(tt_db[4]).strftime('%d.%m'))
                opt.append(tt_db[2])

            opt.append([t.strftime('%H:%M') for t in tt_db[1]])
            cs = list(set([tt.title for tt in tt_db[3]]))
            # days_week = list(set([tt.day_of_week for tt in tts]))

            cse = '/'.join(cs)
            bot.send_message(chat_id=message.chat.id, 
                            text=f"Здравствуйте, уважаемые родители! Ждем вас на {cse} по расписанию")
            
            options = list(np.array(opt).transpose())
            options = [', '.join(op) for op in options]
            options.append('Пропустим')
        
            # создать опрос
            mes = bot.send_poll(chat_id=message.chat.id, 
                        question=text,
                        options=options,
                        is_anonymous=False,
                        allows_multiple_answers=True)
            # внести в бд


                #             tt_db[0].append(tt.pk)
                # tt_db[4].append(datetime.today() + timedelta(week.index(tt.day_of_week) - datetime.today().weekday()))
            
            PollTgbot.objects.create(poll_id=mes.poll.id,
                                    options=dict(zip(list(range(len(tt_db[0]))), zip(tt_db[0], [t.strftime('%d.%m.%Y') for t in tt_db[4]]))))


@bot.poll_answer_handler()
def register_booking(quiz_answer):
    quiz_id = quiz_answer.poll_id # "5397681689478563793"
    quiz_us = quiz_answer.user.id # 1221744722
    quiz_opt = quiz_answer.option_ids # [1], при отмене голоса также приходит poll, в нем 'option_ids': []
    poll = PollTgbot.objects.get(poll_id=quiz_id).options
    client = Client.objects.filter(tg_id=quiz_us)
    if client:
        if len(client) == 1:      # 1 ученик на несколько занятий    
            for i in quiz_opt:
                if str(i) in poll.keys():
                    # print(poll[str(i)][1]) 
                    VisitFix.objects.create(
                        id_client = client[0],
                        id_timetable = Timetable.objects.get(pk=poll[str(i)][0]),
                        date = datetime.strptime(poll[str(i)][1], '%d.%m.%Y'),
                        reserv = True,
                        visit=False
                    )
        else:
            for opt in quiz_opt:
                # найти последнюю запись
                tt = Timetable.objects.get(pk=poll[str(opt)][0])

                for cl in client:
                    last = VisitFix.objects.filter(id_timetable=tt, 
                                                   id_client=cl, 
                                                   date__gt=datetime.today()-timedelta(14))
                    if last:
                        VisitFix.objects.create(
                            id_client = cl,
                            id_timetable = Timetable.objects.get(pk=poll[str(opt)][0]),
                            date = datetime.strptime(poll[str(opt)][1], '%d.%m.%Y'),
                            reserv = True,
                            visit=False
                        )
                    else:
                        print('нужно сообщение с уточнением')


def parse_data(data):
    data = data.split('&')
    res = {'event': data[0]}
    for item in data[1:]:
        k, v = item.split('=')
        res[k] = v
    return res
        
@bot.callback_query_handler(func=lambda callback: True)
def on_click(callback):
    # print(callback)
    if callback.data == 'teacher':
        start_teacher(callback.message)

    elif callback.data[0] == '?':
        data = parse_data(callback.data)
        if data['event'] == '?present':
            bob = VisitFix.objects.get(id=int(data['id']))
            bob.visit = True
            bob.save()
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        if data['event'] == '?absent':
            bob = VisitFix.objects.get(id=int(data['id']))
            bob.reserv = False
            bob.save()
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data[:7] == 'course=':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        # bot.send_message(chat_id=callback.message.chat.id, 
        #                     text=callback.data.split('_')[1])
        check_branch(callback.message, course = int(callback.data.split('=')[1]))
    elif callback.data[:7] == '&branch':
        data = parse_data(callback.data)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        # bot.send_message(chat_id=callback.message.chat.id, 
        #                     text=callback.data.split('_')[1])
        findTTgroup(int(data['course']),int(data['branch']),callback.message.chat.id)

def findTTgroup(course, branch, tg_id):
    # tt = Timetable.objects.filter(id_course__pk=course,
    #                               id_branch__pk=branch)
    tt = Timetable.objects.filter(active=True, tg_id=None)
    if course != -1:
        tt = tt.filter(id_course__id=course)
    if branch != -1:
        tt = tt.filter(id_branch__id=branch)
    for t in tt:
        t.tg_id = tg_id
        t.save()

def check_branch(message: Message, course: int):
    branches = Branch.objects.filter(is_active=True)
    # + не имеет значения
    btns = []
    markup = InlineKeyboardMarkup()
    for br in branches:
        btns.append(InlineKeyboardButton(br.title,
                                            callback_data=f'&branch={br.pk}&course={course}'))
    btns.append(InlineKeyboardButton('Не имеет значения',
                                            callback_data=f'&branch=-1&course={course}'))
    for i in range(len(btns)//3):
        markup.row(btns[i*3], btns[i*3+1], btns[i*3+2])

    if (len(btns) - (i+1)*3) == 1:
        markup.row(btns[-1])
    elif (len(btns) - i*3) == 2:
        markup.row(btns[-2], btns[-1])

    bot.send_message(chat_id=message.chat.id, 
                    text='В каком филиале?',
                    reply_markup=markup)

def start_teacher(message: Message):
    global reg
    reg = True
    try:
        teacher = Teacher.objects.get(tg_id=message.chat.id)
        if teacher.user_id:
            bot.send_message(chat_id=message.chat.id, 
                            text=f'''Здравствуйте, {teacher.last_name} {teacher.first_name}. Вы зарегистрированы на сайте. Для ознакомления с возможностями введите команду /info''')
            reg = False
        else:
            bot.send_message(chat_id=message.chat.id, 
                            text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Пройдите регистрацию')
            bot.send_message(chat_id=message.chat.id, 
                            text=f'Для регистрации на сайте введите логин.')
            bot.register_next_step_handler(message, enter_login, teacher=teacher)

    except ObjectDoesNotExist:
        
        # получить юзернейм, найти в базе
        try:
            teacher = Teacher.objects.get(tg_name="@"+message.chat.username)
            teacher.tg_id = message.chat.id
            teacher.save()
            if teacher.user_id:
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Вы зарегистрированы на сайте. Для ознакомления с возможностями введите команду /info')
                reg = False
            else:
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Пройдите регистрацию')
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Для регистрации на сайте введите логин.')
                bot.register_next_step_handler(message, enter_login, teacher=teacher)

            
        except ObjectDoesNotExist:
            
            teachers = Teacher.objects.filter(tg_id__isnull=True).filter(last_name=message.chat.last_name)
            if len(teachers) == 1:
                teacher = teachers[0]
                del teachers
                teacher.tg_id = message.chat.id
                # teacher.save()
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Здравствуйте, {teacher.last_name} {teacher.first_name}. Пройдите регистрацию')
                bot.send_message(chat_id=message.chat.id, 
                                text=f'Для регистрации на сайте введите логин.')
                print('login')
                bot.register_next_step_handler(message, enter_login, teacher=teacher)
            else:
                bot.send_message(chat_id=message.chat.id, 
                                text='К сожалению, я не могу идентифицировать Вас по имени пользователя. Введите Вашу фамилию')
                bot.register_next_step_handler(message, check_name)

def check_name(message: Message):
    teacher = Teacher.objects.filter(tg_id__isnull=True).filter(last_name=message.text.capitalize())
    if not teacher:
        bot.reply_to(message=message, 
                     text='Я не нашел такой фамилии в списке преподавателей. Возможно, в наборе была допущена ошибка.\n\n\
Проверьте свой ввод и если нужно, повторите сначала. Если ошибок не было допущено, обратитесь к администратору')
        reg = False
    elif len(teacher) == 1:
        teacher[0].tg_id = message.chat.id
        teacher[0].tg_name = message.chat.username
        teacher[0].save()
        bot.send_message(chat_id=message.chat.id, 
                        text=f'Здравствуйте, {teacher[0].last_name} {teacher[0].first_name}. Пройдите регистрацию')
        bot.send_message(chat_id=message.chat.id, 
                        text=f'Для регистрации в портале введите логин.')
        bot.register_next_step_handler(message, enter_login, teacher=teacher[0])

    else:
        bot.reply_to(message=message, 
                     text='''К сожалению, я не могу идентифицировать Вас по фамилии. Создайте имя пользователя в телеграм и передайте его администратору.''')

def enter_login(message: Message, teacher: Teacher):
    login = message.text
    print(message.entities)
    if message.entities:
        print('stoped')
        return
    print(login)
    # Проверка валидности
    if not re.fullmatch(r'[0-9a-zA-Z_-]{5,}', login):
        bot.send_message(chat_id=message.chat.id, text=f'''Имя пользавателя должно включать не меньше 5 латинских символов, цифр, дефис и знак подчеркивания. Попробуйте еще раз''')
        bot.register_next_step_handler(message, enter_login, teacher=teacher)
    # проверка уникальности
    elif User.objects.filter(username=login):
        bot.send_message(chat_id=message.chat.id, text=f'Такой логин уже существует. Попробуйте еще раз')
        bot.register_next_step_handler(message, enter_login, teacher=teacher)
    else:
        bot.send_message(chat_id=message.chat.id, 
                    text=f'Введите пароль.')
        print('Password')
        bot.register_next_step_handler(message, enter_password, teacher=teacher, login=login)

def enter_password(message: Message, teacher: Teacher, login: str):
    if not reg:
        return
    print('passed')
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
    text = 'Для работы используйте следующие команды: \n'
    text += '/list - получить списки учеников на ближайшие занятия\n'
    text += '/visit - отметить присутствующих\n'
    text += '/pay - внести оплату на руки\n'
    bot.send_message(chat_id=message.chat.id, text=text)
    # print(message.json)


def get_booking(tg_id, past=False):
    if past:
        bookings = VisitFix.objects.filter(date__lte=datetime.today()).filter(reserv=True)\
                .filter(visit=False).filter(id_timetable__id_teacher__tg_id=tg_id)
    else:
        bookings = VisitFix.objects.filter(date__gte=datetime.today()).filter(reserv=True)\
                .filter(visit=False).filter(id_timetable__id_teacher__tg_id=tg_id)
    # отобрать только этого препода сортировать по дате, времени
    lst = {}
    for booking in bookings:
        timestamp = datetime.timestamp(datetime.combine(booking.date, booking.id_timetable.timetb))

        if not past and timestamp < datetime.timestamp(datetime.now()):
            continue
        if past and timestamp > datetime.timestamp(datetime.now()):
            continue
        if not(timestamp in lst.keys()):
            lst[timestamp] = []
        lst[timestamp].append((booking.pk, booking.id_client.surname + ' ' + booking.id_client.name))
    return lst

@bot.message_handler(commands=['list'])
def echo(message: Message):
    '''получение запланированных занятий и списка учеников'''
    text = 'На данный момент у Вас запланированы следующие занятия:'
    # получить список из брони, все занятия, где есть хоть 1 бронь
    lst = get_booking(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text=text)
    # # сортируем по дате timestamp
    # locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    # for timestamp, names in sorted(lst.items()):
    #     text = f"<b>{datetime.fromtimestamp(timestamp).strftime('%d.%m, %a, %H:%M')}</b>\n"
    #     for cl in names:
    #         text += cl[1] + '\n'
    #     bot.send_message(chat_id=message.chat.id, text=text, parse_mode='HTML')
    for timestamp, names in sorted(lst.items()):
        # Устанавливаем локаль только для данного блока кода
        with locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8'):
            text = f"<b>{datetime.fromtimestamp(timestamp).strftime('%d.%m, %a, %H:%M')}</b>\n"
            for cl in names:
                text += cl[1] + '\n'
            bot.send_message(chat_id=message.chat.id, text=text, parse_mode='HTML')
    
@bot.message_handler(commands=['visit'])
def echo(message: Message):
    '''отметить присутствовавших'''
    lst = get_booking(message.chat.id, past=True)
    for timestamp, names in sorted(lst.items()):
        text = f"<b>{datetime.fromtimestamp(timestamp).strftime('%d.%m, %a, %H:%M')}</b>\n"
        bot.send_message(chat_id=message.chat.id, text=text, parse_mode='HTML')
        for cl in  names:
            markup = InlineKeyboardMarkup()
            btn1 = InlineKeyboardButton('Присутствовал',callback_data=f'?present&id={cl[0]}')
            btn2 = InlineKeyboardButton('Отсутсвовал',callback_data=f'?absent&id={cl[0]}')
            markup.row(btn1, btn2)
            bot.send_message(chat_id=message.chat.id, 
                            text=cl[1],
                            reply_markup=markup)


@bot.message_handler(commands=['pay'])
def get_pay(message: Message):
    if message.chat.type == 'private':
        teacher = Teacher.objects.get(tg_id=message.chat.id)
        if teacher:
            bot.send_message(chat_id=message.chat.id, 
                text=f'Введите фамилию ученика и внесенную сумму.\n *Образец: Иванов 1100*\n')
            bot.register_next_step_handler(message, enter_pay, teacher=teacher)

def enter_pay(message: Message, teacher: Teacher, last_name=None, summa=None):
    data = message.text.split()
    # print(data)
    # найти в базе ученика
    if not summa:
        try:
            summa = data[1]
            try:
                summa = int(summa)
            except:
                bot.send_message(chat_id=message.chat.id, 
                    text=f'Ошибка при внесении оплаты. Введите корректно информацию')
                return
        except:
            bot.send_message(chat_id=message.chat.id, 
                text=f'Команда прерврана')
    
    if last_name:
        clients = Client.objects.filter(surname=last_name, name=data[0].capitalize())
    else:
        clients = Client.objects.filter(surname=data[0].capitalize())
    if clients:
        if len(clients) == 1:
            # найти бронь
            booking = VisitFix.objects.get(id_client=clients[0],
                                              date__gte=datetime.today(),
                                              id_timetable__id_teacher=teacher)
            if booking:
                # print(booking)
                # добавить сумму в -зп
                if summa == booking.id_timetable.sum_one:
                    subscription = 1
                elif summa == booking.id_timetable.sum_abon:
                    subscription = 4
                else:
                    subscription = int(summa/booking.id_timetable.sum_one)
                Paying.objects.create(id_client=booking.id_client, 
                                      id_course=booking.id_timetable.id_course, 
                                      id_branch=booking.id_timetable.id_branch,
                                      date=datetime.now(),
                                      summ=summa,
                                      subscription=subscription, 
                                      accepted_payment=teacher)


                # 
                bot.send_message(chat_id=message.chat.id, 
                    text=f'Оплата добавлена')
            else:
                bot.send_message(chat_id=message.chat.id, 
                    text=f'Ошибка при внесении оплаты. Решите этот вопрос через администратора')
        else:
            if not last_name:
                bot.send_message(chat_id=message.chat.id, 
                    text=f'Фамилия неуникальна. Введите имя')

                bot.register_next_step_handler(message, enter_pay, 
                                               teacher=teacher, 
                                               last_name=data[0].capitalize(),
                                               summa=summa)

            else:
                bot.send_message(chat_id=message.chat.id, 
                    text=f'Не удалось определить ученика')
    else:
        bot.send_message(chat_id=message.chat.id, 
            text=f'Не удалось найти в базе {data[0].capitalize()}')



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