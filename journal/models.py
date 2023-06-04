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
    id_teacher = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name = 'Преподаватель')
    id_course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name = 'Предмет')
    id_branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL, verbose_name = 'Филиал')
    day_of_week = models.CharField(max_length=30, choices = CHOICES, verbose_name = 'День недели')
    timetb = models.TimeField(verbose_name = 'Время')
    duration = models.DecimalField(default=2.0,max_digits=2, decimal_places=1, verbose_name = 'Длительность')
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
    phone_regex = RegexValidator(regex=r"^\+(?:[0-9]●?){6,14}[0-9]$", message=("Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name='Контакт')
    
    active = models.BooleanField(default=True, verbose_name='Активный')

    # Metadata
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ['active','surname']      
    
    def __str__(self):
        return self.surname + ' ' + self.name
  
class Teacher(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    contact = models.CharField(max_length=150)
    user_id = models.ForeignKey(User, related_name='user', on_delete=models.SET_NULL, null=True, blank=True, )
    tg_name = models.CharField(max_length=150)
    tg_id = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.last_name



# фикс зарплат
class Salary(models.Model):
    id_teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Преподаватель')
    last_sum = models.IntegerField(default=0, verbose_name = 'Сумма за час')
    date_of_change = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сумма"
        verbose_name_plural = "Зарплата"
        ordering = ["-date_of_change",'id_teacher']        


class TeacherJournal(models.Model):
    id_teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Преподаватель')
    id_course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name = 'Предмет')
    id_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name = 'Филиал')
    date_of_visit = models.DateField(verbose_name = 'Дата')
    time_of_visit = models.TimeField(verbose_name = 'Время',default='15:00:00')
    number_hours = models.DecimalField(default=2, max_digits=2, decimal_places=1, verbose_name = 'Количество часов')
    date_of_paid = models.DateField(verbose_name = 'Дата выплаты', auto_now=True)
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
    payed = models.ForeignKey(Paying, null=True, on_delete=models.SET(False), verbose_name = 'Дата оплаты')

    # Metadata
    class Meta:
        verbose_name = "Посещение"
        verbose_name_plural = "Посещение"
        ordering = ['date']      
