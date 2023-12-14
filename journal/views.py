import json
from urllib import request
import re

# from ast import Delete
# from calendar import week
import datetime
from datetime import timedelta

from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DeleteView, ListView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import permission_required
from django.db.models.aggregates import Max, Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import F
from django.utils import timezone

from .models import *
from .forms import *
from .tools import *


def reg_exp_phone(input_data):
    # 79263441280
    # +79253441280
    # 9253441280
    # 89253441280
    # 8-925-344-12-80
    # (925)344-1280

    # убрать все не цифры
    inp = re.sub(r'\D', '', input_data)
    if len(inp) == 11:
        return '7' + inp[1:]
    if len(inp) == 10:
        return '7' + inp
    return input_data

def reg_exp_telegram(input_data):
    return input_data.lstrip('@').replace('https://t.me/', '')

class BranchView(ListView):
    model = Branch
    form_class = AddBranchForm
    success_url = ''

    def get(self, request, *args, **kwargs):        
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return super(self.__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        return Branch.objects.all()

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.get(request)


class CourseView(ListView):
    model = Course
    form_class = AddCourseForm
    success_url = ''

    def get(self, request, *args, **kwargs):        
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return super(self.__class__, self).get(self, request, *args, **kwargs)
        
    def get_queryset(self):
        return Course.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.get(request)
        
    # def post(self,request):
    #     # print(request.POST)
    #     user = request.user
    #     form = AddCourseForm(request.POST)
    #     if form.is_valid():
    #         form = form.save(commit=False)
    #         form.id_teacher_id = user.id
    #         form.save()
    #     return redirect('workingtime')
    

class ClientView(ListView):
    model = Client
    form_class = AddClientForm
    success_url = ''

    def get(self, request, *args, **kwargs):        
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return super(self.__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        return Client.objects.all()

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.get(request)


class LoginView(View):

    def get(self,request):
        if request.user.is_authenticated:
            return redirect('timetable')
        else:
            return redirect('accounts/login')


class TimetableView(View):

    def get(self,request,t_id=0,br_id=0):

        if not request.user.is_authenticated:
            return redirect('login')
        
        allweek = ['ПН','ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        d = [{'dw':'ПН','tt':[]},
            {'dw':'ВТ','tt':[]},
            {'dw':'СР','tt':[]},
            {'dw':'ЧТ','tt':[]},
            {'dw':'ПТ','tt':[]},
            {'dw':'СБ','tt':[]},
            {'dw':'ВС','tt':[]}]
#        for dw in allweek:
#            d['dw'] = Timetable.objects.filter('day_of_week'==dw)
#        tt = Timetable.objects.filter(day_of_week__contains = 'ЧТ')
        teachers = Teacher.objects.filter(is_active=True)
        branchs = Branch.objects.all()
        form = AddTimetableForm()
        

#        tt = Timetable.objects.order_by('timetb','id_branch','day_of_week')
        tt = Timetable.objects.filter(active=True)
        if br_id:
            tt = tt.filter(id_branch=br_id)
        if t_id:
            tt = tt.filter(id_teacher=t_id)
        tt = tt.order_by('timetb')

        # if br_id:
        #     tt = Timetable.objects.filter(id_branch=br_id, active=True)
        # else:
        #     tt = Timetable.objects.filter(active=True)


        for it in tt:
            # bbr = it.id_branch
            # if it.id_branch.title not in d[allweek.index(it.day_of_week)]['tt'].keys():
            #     d[allweek.index(it.day_of_week)]['tt'][it.id_branch.title] = []
            d[allweek.index(it.day_of_week)]['tt'].append(it)

        data = {'title':'Расписание', 
                'timetable':tt, 
                'branchs':branchs, 
                'teachers':teachers, 
                't': t_id,
                'b': br_id,
                'd':d, 
                'form':form}

        return render(request, 'journal/timetable.html', data)

    def post(self, request):
        if request.POST['action'] == 'add':
            # print('added')
            # res = Timetable.objects.get(
            #     id_teacher=request.POST['id_teacher'], 
            #     id_course=request.POST['id_course'], 
            #     id_branch=request.POST['id_branch'], 
            #     day_of_week=request.POST['day_of_week'], 
            #     timetb=request.POST['timetb']
            #     )
            # if res:
            #     res.active = True
            #     res.save()

            form = AddTimetableForm(request.POST)
            form.save()


        if request.POST['action'] == 'del':
            pk = request.POST['pk']
            bob = Timetable.objects.get(id=pk)
            bob.active = False
            bob.save()
        # post на удаление записи в расписании. Удалить - перевести active в False
        return redirect('/')


class TeacherView(View):
    def get(self,request):

        if not request.user.is_authenticated:
            return redirect('login')

        active = Teacher.objects.filter(is_active=True).exclude(user_id=None)
        notactive = Teacher.objects.filter(is_active=False)
        new = Teacher.objects.filter(is_active=True, user_id=None)

        form = AddTeacherForm()
        if request.POST:
            form = AddTeacherForm(request.POST)

        return render(request,'journal/teacherlist.html', {'active': active, 
                                                           'notactive':notactive,
                                                           'new': new,
                                                           'form': form,
                                                           })
    

    def post(self, request):
        if request.POST['action'] == 'add':
            data = {}
            data['first_name'] = request.POST['first_name']
            data['last_name'] = request.POST['last_name']
            data['contact'] = request.POST['contact']
            data['tg_name'] = request.POST['tg_name']

            form = AddTeacherForm(data)
            if form.is_valid():
                form.save()
            else:
                data['contact'] = reg_exp_phone(data['contact'])
                data['tg_name'] = reg_exp_telegram(data['tg_name'])
                form = AddTeacherForm(data)
                if form.is_valid():
                    form.save()
                else:
                    print('form error')
                    return self.get(request)
            
        if request.POST['action'] == 'del':
            pk = request.POST['pk']
            bob = Teacher.objects.get(id=pk)
            bob.is_active = False
            bob.save()
        # post на удаление записи в расписании. Удалить - перевести active в False
        if request.POST['action'] == 'rem':
            pk = request.POST['pk']
            bob = Teacher.objects.get(id=pk)
            bob.is_active = True
            bob.save()
        return redirect('teacherlist')


class WorkingTimeView(View):

    def get(self,request):

        if not request.user.is_authenticated:
            return redirect('login')

        # br = User.objects.get(pk=1)
        # print(br)
        # d = {'id_teacher':br, 'last_sum':650}
        # Salary.objects.create(**d)

        user = request.user
        print(user)
        
        allwt = TeacherJournal.objects.filter(ispaid = False, id_teacher__user_id=user)

        total = 0
        for wt in allwt:
            total += wt.number_hours

        
        
        return render(request,'journal/workingtime.html',{'journal': allwt, 'total':total})

class AddWorkingTimeView(View):

    def post(self,request):
        # print(request.POST)
        user = request.user
        form = AddWorkingTimeForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.id_teacher_id = user.id
            form.save()
        return redirect('workingtime')


class DellWorkingTimeView(DeleteView):
    model=TeacherJournal
    success_url='/workingtime/'


class TeacherSizePaidView(View):
    def get(self,request):

        if not request.user.is_authenticated:
            return redirect('login')

        # вывести только просмотр
        sal_raw = Salary.get_list_salary()
        for el in sal_raw:
            print(el)
        return render(request,'journal/price.html', {'data': sal_raw})
    
    def post(self, request):
        data = json.load(request)
        res = []
        for id in data['lst']:
            tom = Salary.objects.create(
                id_teacher = Teacher.objects.get(pk=int(id)),
                last_sum = int(data['sum']),
                date_of_activate = data['bdate']
            )
            res.append(tom.id)
        return JsonResponse({'res': res})
    

class SalaryView(View):
    def get(self, request):

        if not request.user.is_authenticated:
            return redirect('login')

        data = {}
        # список действующих работников
        teachers = Teacher.objects.filter(is_active=True)
        for teacher in teachers:
            data[teacher.id] ={'id': teacher.id, 'last_name': teacher.last_name, 'first_name': teacher.first_name, 'first_date': datetime.date.today(), 'tt': [], 'hp': []}
        # список неопл занятий
        wt = TeacherJournal.objects.filter(ispaid=False)
        for item in wt:
            r = Salary.objects.filter(date_of_activate__lte=item.date_of_visit, id_teacher=item.id_teacher).order_by('date_of_activate').last()

            item.last_sum = r.last_sum  if r else 0
            item.total = item.last_sum * item.number_hours
            data[item.id_teacher.id]['tt'].append(item)
            if item.date_of_visit < data[item.id_teacher.id]['first_date']:
                data[item.id_teacher.id]['first_date'] = item.date_of_visit



        # print(data)    
        # получить список оплат занятий на руки
        for t_id, d in data.items():
            pays = Paying.objects.filter(accepted_payment__pk=t_id, date__gte=d['first_date'])
            if pays:
                data[item.id_teacher.id]['hp'] = pays
        print(data)
        content = {
            'data': data.values(), # список преподов, сумма к выплате, + подсписок с расшифровкой
        }


        return render(request,'journal/salary.html', content)
    
    def post(self, request):
        data = json.load(request)
        print(data)
        res = list(map(int, data['lst']))
        print(res)
        TeacherJournal.objects.filter(pk__in=res).update(ispaid=True, date_of_paid=datetime.datetime.today())
        return JsonResponse({'res': res})
        

class TeacherPaidViev(View):
    def get(self,request):
        pass

class BookingView(View):
    def get(self,request,br_id,course):

        if not request.user.is_authenticated:
            return redirect('login')

    # из графика достать следующие варианты на всю неделю
        tt = Timetable.objects.filter(active=True)
        if br_id:
            tt = tt.filter(id_branch = br_id)
        if course:
            tt = tt.filter(id_course = course)

        #даты на ближайшую неделю
        week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        wd = datetime.datetime.today().weekday()
        sweek = week[wd:]+week[:wd]
        dweek = dict()
        for id in range(len(sweek)):
            dweek[sweek[id]] = datetime.datetime.today()+timedelta(id)

        ttt = []
        for t in tt:
            ttd = dict()
            ttd['id']=t.id
            ttd['id_teacher']=t.id_teacher
            ttd['id_course']=t.id_course
            ttd['id_branch']=t.id_branch
            ttd['day_of_week']=t.day_of_week
            ttd['timetb']=t.timetb
            ttd['duration']=t.duration
            ttd['active']=t.active
            ttd['date']=dweek[t.day_of_week]
            ttt.append(ttd)
        # достать все записи из посещений по id_tt
        visits = VisitFix.objects.filter(id_timetable__in=tt)
        booking = visits.filter(date__gte=datetime.datetime.today()).filter(reserv=True)
        booking_lst = [x.id_client.id for x in booking]
        visits_last = visits.filter(date__lt=datetime.datetime.today()).values(
            'id_client__id',
            'id_client__name',
            'id_client__surname',
            'id_timetable_id__id_course__title',
            'id_timetable_id__id_branch__title',
            'id_timetable_id__timetb'
            ).annotate(total=Max('date')).order_by('id_client__surname')
        
        visits = [vis for vis in visits_last if not(vis['id_client__id'] in booking_lst)]
        # for vis in visits_last:
        #     print(vis['id_client__id'])
        #     print(vis['id_client__id'] in booking_lst)
        newpeople = Client.objects.filter(active=True).order_by('surname').exclude(pk__in=VisitFix.objects.all().values('id_client'))
        data=dict()
        clients = Client.objects.filter()
        branchs = Branch.objects.all()
        courses = Course.objects.all()
        data['clients'] = clients
        data['courses'] = courses
        data['branchs'] = branchs
        data['course'] = course
        data['br'] = br_id
        data['booking'] = booking
        data['visits'] = visits
        data['newpeople'] = newpeople
        data['tt'] = ttt

        formb = AddBookingForm()
        data['form'] = formb

        return render(request,'journal/booking.html',data)

        

    def post(self,request,br_id,course):
        if request.POST['action'] == 'add':
            id_client = request.POST['id_client']
            id_timetable = request.POST['id_timetable']
            date = request.POST['date']
            # try:
            cl = Client.objects.get(pk=id_client)
            tb = Timetable.objects.get(pk=id_timetable)
            check = VisitFix.objects.filter(id_client=cl, id_timetable=tb, date=date)
            if not check:
                VisitFix.objects.create(id_client=cl, id_timetable=tb, date=date, reserv=True, visit=False)
        if request.POST['action'] == 'del':
            id_booking = request.POST['id_booking']
            VisitFix.objects.get(pk=id_booking).delete()

        return redirect(request.META.get('HTTP_REFERER'), '/booking/0/0')


class VisitPayView(View):
    def get(self, request):

        if not request.user.is_authenticated:
            return redirect('login')

        form = AddPayingForm()
        # pj = Paying.objects.values('id_client__surname', 'id_client__name', 'id_course__title').annotate(Max('date'))
        pj = Paying.objects.values('id_client__surname', 'id_client__name', 'id_course__title').annotate(last_pay=Max('date'), lost=Sum(F('subscription')) - Sum(F('used_lesson')))
        for o in pj:
            print(o)
        return render(request,'journal/paying.html', {'journal': pj,'form': form})
    
    def post(self, request):
        form = AddPayingForm(request.POST)
        # если пробное бесплатно

        # проверить долг
        client = request.POST['id_client']
        course = request.POST['id_course']
        # если есть долг записать даты в те занятия в долг
        dolg = Paying.objects.filter(id_client=client, id_course=course).last()
        if dolg:
            if dolg.subscription < dolg.used_lesson:
                form = form.save(commit=False)
                form.used_lesson = (dolg.used_lesson - dolg.subscription)
                dolg.used_lesson = F('subscription')
                dolg.save()
        form.save()
        return redirect(f'/visitors/paying')


class VisitorsView(View):
    # посещение может отмечать действующий препод
    def get(self,request,br_id,course):
        
        if not request.user.is_authenticated:
            return redirect('login')

        # получить расписание только для текущего препода
        user = request.user
        try:
            teacher = Teacher.objects.get(user_id=user)
        except:
            return redirect('teacherlist')

        tt = Timetable.objects.filter(active=True).filter(id_teacher = teacher)

        # найти все брони на эти расписания, но раньше текущего времени

        booking = VisitFix.objects.filter(reserv=True, visit=False, id_timetable__id_teacher=teacher, date__lte=datetime.datetime.now()).order_by('date')
        if br_id:
            booking = booking.filter(id_timetable__id_branch = br_id)
        if course:
            booking = booking.filter(id_timetable__id_course = course)

        data=dict()
        branchs = Branch.objects.all()
        courses = Course.objects.all()
        data['courses'] = courses
        data['branchs'] = branchs
        data['course'] = course
        data['br'] = br_id
        data['tt'] = tt
        data['booking'] = booking
 
        return render(request,'journal/visitors.html',data)
    
    def post(self, request,br_id,course):
        if request.POST['action'] == 'add':
            pk = request.POST['pk']
            bob = VisitFix.objects.get(id=pk)
            bob.visit = True
            # найти последнюю оплату и +1 к used_lesson
            pay = Paying.objects.filter(id_client=bob.id_client, id_course=bob.id_timetable.id_course).last()
            if pay:
                pay.used_lesson=F('used_lesson')+1
            else:
                pay = Paying(
                    id_client = bob.id_client,
                    id_course = bob.id_timetable.id_course,
                    id_branch = bob.id_timetable.id_branch,
                    summ = 0,
                    subscription = 0,
                    used_lesson = 1
                )
            pay.save()
            bob.save()
            # проверить наличие записи в рабочих часах
            # дата, препод, время, курс
            teacher_fix = TeacherJournal.objects.filter(id_teacher=bob.id_timetable.id_teacher,
                                                        date_of_visit=bob.date,
                                                        time_of_visit=bob.id_timetable.timetb,
                                                        id_course=bob.id_timetable.id_course)
            if not teacher_fix:
                # проверить более 1 присутствующего
                les = VisitFix.objects.filter(id_timetable=bob.id_timetable, date=bob.date)
                if len(les) > 1:
                    # добавить запись в таблицу учителя
                    TeacherJournal.objects.create(
                        id_teacher = bob.id_timetable.id_teacher,
                        id_course = bob.id_timetable.id_course,
                        id_branch = bob.id_timetable.id_branch,
                        date_of_visit = bob.date,
                        time_of_visit = bob.id_timetable.timetb,
                        number_hours = bob.id_timetable.hours_payed
                        )


        if request.POST['action'] == 'del':
            pk = request.POST['pk']
            bob = VisitFix.objects.get(id=pk)
            bob.reserv = False
            bob.save()

            # запустить бота, предупредить завуча
            # проверить оплаты:
            # pay = Paying.objects.filter(id_client=bob.id_client, id_course=bob.id_timetable.id_course).last()
            # если ничего не оплачено, то игнор
            # если оплачен разовый сеанс,то игнор
            # если абонемент, то предупреждать
            # if pay:
            #     if pay.subscription > 1 and pay.subscription > pay.used_lesson:
            #         pass

        return redirect(f'/visitors/{br_id}/{course}')

class ComputersView(ListView):
    model = Computers
    # form_class = AddComputerForm
    success_url = ''

    def get(self, request, *args, **kwargs):        
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return super(self.__class__, self).get(self, request, *args, **kwargs)
        
    def get_queryset(self):
        return Computers.objects.all()
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            
        return self.get(request)

class ImportView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        elif not request.user.is_superuser:
            return redirect('/')
        form = ImportExcel()
        data = {'form': form}
        return render(request,'journal/import.html',data)

    def post(self, request):
        if request.POST:
            form = ImportExcel(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES.get('file')
                uploading_file = Import({"file": file})
                result = uploading_file.add_clients()
                if not result:
                    messages.success(request, 'Успешная загрузка')
        else:
            for error in result:
                messages.error(request, error)
        return self.get(request)






# Пятница 15:00, 16:00 шашки Гриша
# Воскресенье 11:00-13:00 математика Огэ Трохин
# Онлайн 11:00-12:30 воскреснье Савицкий