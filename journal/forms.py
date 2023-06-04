from dataclasses import fields
from email.policy import default
#from pyexpat import model
# from tkinter import Widget
#from turtle import textinput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,UserChangeForm
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget,AdminTimeWidget
from django.forms.widgets import NumberInput
from .fields import MyModelChoiceField


from django import forms
#from django.utils.translation import ugettext_lazy as ugl
from .models import *


WORKING_TIMES = [
    ('10:00:00', '10:00'),
    ('10:30:00', '10:30'),
    ('11:00:00', '11:00'),
    ('11:30:00', '11:30'),
    ('12:00:00', '12:00'),
    ('12:30:00', '12:30'),
    ('13:00:00', '13:00'),
    ('13:30:00', '13:30'),
    ('14:00:00', '14:00'),
    ('14:00:00', '14:00'),
    ('14:30:00', '14:30'),
    ('15:00:00', '15:00'),
    ('15:30:00', '15:30'),
    ('16:00:00', '16:00'),
    ('16:30:00', '16:30'),
    ('17:00:00', '17:00'),
    ('17:30:00', '17:30'),
    ('18:00:00', '18:00'),
    ('18:30:00', '18:30'),
]
class testForm(forms.Form):
    date1 = MyModelChoiceField(queryset=TeacherJournal.objects.all().order_by('date_of_visit'), label='Дата1')

class createUserForm(UserCreationForm):

    first_name= forms.CharField(label='Имя',widget=forms.TextInput(attrs={'class':'form_control'}))
    last_name= forms.CharField(label='Фамилия',widget=forms.TextInput(attrs={'class':'form_control'}))
    email= forms.EmailField(widget=forms.EmailInput(attrs={'class':'form_control'}))

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields  + ('first_name', 'last_name', 'email')


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

class authUserForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class AddTimetableForm(forms.ModelForm):
    
    class Meta:
        model = Timetable
        # fields = '__all__'
        fields = ['id_course', 'id_branch', 'day_of_week','timetb', 'duration', 'id_teacher']
        widgets = {
                'id_teacher': forms.Select(),
                'id_course': forms.Select(),
                'id_branch': forms.Select(),
                'day_of_week': forms.Select(),
                'timetb': forms.Select(choices=WORKING_TIMES),
                'duration': forms.NumberInput(attrs={'size': '2'}),
        }


class AddWorkingTimeForm(forms.ModelForm):

    class Meta:
        model = TeacherJournal
        # fields = '__all__'
        fields = ['id_course', 'id_branch', 'date_of_visit','time_of_visit', 'number_hours']
        widgets = {
                # 'id_teacher': forms.TextInput(),
                'id_course': forms.Select(),
                'id_branch': forms.Select(),
                'date_of_visit': AdminDateWidget(),
                'time_of_visit': AdminTimeWidget(),
                'number_hours': forms.NumberInput(attrs={'size': '2'}),
        }

class AddBookingForm(forms.Form):
    id_client = forms.CharField(widget=forms.HiddenInput)
    id_timetable = forms.CharField(widget=forms.HiddenInput)
    date = forms.CharField(widget=forms.HiddenInput)
    reserv = forms.CharField(widget=forms.HiddenInput, initial=1)
    # class Meta:
    #     model = VisitFix
    #     fields = ['id_client', 'id_timetable', 'date', 'reserv']
    #     widgets = {
    #         'id_client':forms.HiddenInput(), 
    #         'id_timetable':forms.HiddenInput(), 
    #         'date':forms.HiddenInput(), 
    #         'reserv':forms.HiddenInput()
    #     }

class AddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        # fields = '__all__'
        fields = ['title']
        widgets = {
                # 'id_teacher': forms.TextInput(),
                'title': forms.TextInput(),
        }

class AddBranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        # fields = '__all__'
        fields = ['title', 'address']
        widgets = {
                # 'id_teacher': forms.TextInput(),
                'title': forms.TextInput(),
                'title': forms.TextInput(),
        }


class AddClientForm(forms.ModelForm):
    class Meta:
        model = Client
        # fields = '__all__'
        fields = ['surname', 'name', 'birthday', 'guardian', 'mobile_phone', 'address']
        widgets = {
            'surname': forms.TextInput(), 
            'name': forms.TextInput(), 
            'birthday': AdminDateWidget(), 
            'guardian': forms.TextInput(), 
            'mobile_phone': forms.TextInput(), 
            'address': forms.TextInput()
        }

    
