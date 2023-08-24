from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.forms import ModelChoiceField
from django.utils.timezone import now


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name = 'Название')
    describe = models.TextField(blank=True, verbose_name = 'Описание')
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.title

    # Metadata
    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["title"]        


class Branch(models.Model):
    title = models.CharField(max_length=200, verbose_name = 'Филиал')
    address = models.CharField(max_length=200, verbose_name = 'Адрес')
    rent = models.IntegerField(default=0, verbose_name = 'Арендная плата')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    # Metadata
    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"
        ordering = ["title"]        

class Teacher(models.Model):
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    phone_regex = RegexValidator(regex=r"^7([0-9]){9}[0-9]$", message=("Номер телефона введен некорректный"))
    contact = models.CharField(validators=[phone_regex], max_length=150, verbose_name='Номер телефона')
    user_id = models.ForeignKey(User, related_name='user', on_delete=models.SET_NULL, null=True, blank=True, )
    tg_name = models.CharField(max_length=150, verbose_name='Имя Telegram', blank=True, null=True, unique=True)
    tg_id = models.CharField(max_length=30, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.last_name
    
    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"
        ordering = ['last_name']        


class Timetable(models.Model):
    CHOICES = (
        ('ПН', 'Понедельник'),
        ('ВТ', 'Вторник'),
        ('СР', 'Среда'),
        ('ЧТ', 'Четверг'),
        ('ПТ', 'Пятница'),
        ('СБ', 'Суббота'),
        ('ВС', 'Воскресенье'),
    )
    id_teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name = 'Преподаватель')
    id_course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name = 'Предмет')
    id_branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL, verbose_name = 'Филиал')
    day_of_week = models.CharField(max_length=30, choices = CHOICES, verbose_name = 'День недели')
    timetb = models.TimeField(verbose_name = 'Время')
    duration = models.DecimalField(default=2.0,max_digits=2, decimal_places=1, verbose_name = 'Длительность')
    hours_payed = models.DecimalField(default=2.0,max_digits=2, decimal_places=1, verbose_name = 'Часов на оплату')
    active = models.BooleanField(verbose_name = 'Включен',default=True)

    def __str__(self):
        return f'{self.id_course} - {self.id_branch} - {self.day_of_week} - {self.timetb}'

    # Metadata
    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Расписание"
        ordering = ['id_teacher','id_course', 'id_branch', 'day_of_week',"timetb"]        


class Client(models.Model):
    surname = models.CharField(max_length=60, verbose_name='Фамилия')
    name = models.CharField(max_length=60, verbose_name='Имя')
    guardian = models.CharField(max_length=200, verbose_name='Родитель') #попечитель
    birthday = models.DateField(verbose_name='Дата рождения')
    address = models.CharField(verbose_name='Место проживания', max_length=200, default='МО')
    phone_regex = RegexValidator(regex=r"^7([0-9]){9}[0-9]$", message=("Номер телефона введен некорректный"))
    mobile_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name='Контакт')
    tg_id = models.CharField(max_length=30, null=True, blank=True, unique=True)
    active = models.BooleanField(default=True, verbose_name='Активный')

    # Metadata
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ['active','surname']      
    
    def __str__(self):
        return self.surname + ' ' + self.name
  

# фикс зарплат
class Salary(models.Model):
    id_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name = 'Преподаватель')
    last_sum = models.IntegerField(default=0, verbose_name = 'Сумма за час')
    date_of_change = models.DateTimeField(auto_now_add=True)
    date_of_activate = models.DateTimeField(verbose_name='Действительна с ')

    class Meta:
        verbose_name = "Сумма"
        verbose_name_plural = "Зарплата"
        ordering = ["-date_of_change",'id_teacher']        

    def get_list_salary():
        sal_raw = Salary.objects.raw('''
            SELECT t1.id, 
            t2.id as teacher_id,  
            date_of_activate, 
            max(date_of_activate) as last_pay, 
            last_sum,
            t2.first_name,
            t2.last_name
            FROM journal_teacher as t2
            LEFT JOIN journal_salary as t1
            on t1.id_teacher_id = t2.id
            WHERE t2.is_active = 1
            GROUP BY teacher_id 
            ORDER BY last_sum
        ''')
        return sal_raw

class TeacherJournal(models.Model):
    id_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name = 'Преподаватель')
    id_course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name = 'Предмет')
    id_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name = 'Филиал')
    date_of_visit = models.DateField(verbose_name = 'Дата')
    time_of_visit = models.TimeField(verbose_name = 'Время',default='15:00:00')
    number_hours = models.DecimalField(default=2, max_digits=2, decimal_places=1, verbose_name = 'Количество часов')
    date_of_paid = models.DateField(verbose_name = 'Дата выплаты', null=True, blank=True)
    ispaid = models.BooleanField(default=False) #оплачен

    class Meta:
        verbose_name = "Рабочие часы"
        verbose_name_plural = "Рабочие часы"
        ordering = ["id_teacher", "-date_of_visit", "-ispaid"]      

    class MyModelChoiceField(ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.date_of_visit


class Paying(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name = 'Ученик')
    id_course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name = 'Предмет')
    id_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name = 'Филиал')
    date = models.DateTimeField(auto_now_add=True, verbose_name = 'Дата оплаты')
    summ = models.IntegerField(verbose_name = 'Сумма')
    subscription = models.IntegerField(default=1, verbose_name = 'Количество занятий') #колво оплаченых занятий
    used_lesson = models.IntegerField(default=0, verbose_name = 'Использовано')


    # Metadata
    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплата"
        ordering = ["date"]      
    

class VisitFix(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name = 'Ученик')
    id_timetable = models.ForeignKey(Timetable,null=True, on_delete=models.CASCADE, verbose_name = 'Расписание')
    date = models.DateField(verbose_name = 'Дата')
    reserv = models.BooleanField(verbose_name = 'Запланирован')
    visit = models.BooleanField(verbose_name = 'Посетил')
    # payed = models.ForeignKey(Paying, null=True, on_delete=models.SET(False), verbose_name = 'Дата оплаты')

    # Metadata
    class Meta:
        verbose_name = "Посещение"
        verbose_name_plural = "Посещение"
        ordering = ['date']      

class Computers(models.Model):
    articul = models.CharField(max_length=10, verbose_name='Номер')
    metka = models.CharField(max_length=3, null=True, blank=True, verbose_name='Метка')
    manufacture = models.CharField(max_length=20, verbose_name='Производитель')
    model = models.CharField(max_length=20, null=True, blank=True, verbose_name='Модель')
    os = models.CharField(max_length=250, verbose_name='Операционная система')
    cpu = models.CharField(max_length=150, verbose_name='Процессор')
    ozu = models.CharField(max_length=60, verbose_name='Оперативная память')
    hdd_sdd = models.CharField(max_length=160, verbose_name='Диски')
    note = models.CharField(max_length=60, null=True, blank=True, verbose_name='Состояние')
    id_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Филиал')
    date_start = models.DateField(verbose_name='Дата покупки/начала эксплуатации')
    data_service = models.DateField(verbose_name='Последнее обслуживание')

    class Meta:
        verbose_name = "Ноутбук"
        verbose_name_plural = "Ноутбуки"
        ordering = ['manufacture', 'id_branch']
