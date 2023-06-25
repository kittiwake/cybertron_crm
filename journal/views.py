import json
from urllib import request

# from ast import Delete
# from calendar import week
from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DeleteView, ListView
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models.aggregates import Max, Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import F
from django.utils import timezone

def registerPage(request):    
    if request.method == 'POST':
        profile_form = createUserForm(request.POST)

        if profile_form.is_valid():
            user = profile_form.save()

            #we don't save the profile_form here because we have to first get the value of profile_form, assign the user to the OneToOneField created in models before we now save the profile_form. 

            messages.success(request,  'Your account has been successfully created')

            return redirect('/')
        # pass
    else:
        profile_form = createUserForm()


    # context = {'form': form, 'profile_form': profile_form}    
    context = {'profile_form': profile_form}    
    return render(request, 'journal/register.html', context)

# def registerNamePage(request):    
#     if request.method == 'POST':
#         change_form =changeUserForm(request.POST)

#         if change_form.is_valid():
#             save_name = change_form.save()

#             #we don't save the profile_form here because we have to first get the value of profile_form, assign the user to the OneToOneField created in models before we now save the profile_form. 

#             messages.success(request,  'Your account has been successfully created')

#             return redirect('login')
#         # pass
#     else:
#         change_form = changeUserForm()


#     # context = {'form': form, 'profile_form': profile_form}    
#     context = {'change_form':change_form}    
#     return render(request, 'journal/change_name.html', context)

class RegisterView(View):

    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            un = form.cleaned_data.get('username')
            up = form.cleaned_data.get('password1')
            user = authenticate(username=un, password=up)
            login(request, user)

            return redirect('timetable')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

class BranchView(ListView):
    model = Branch
    form_class = AddBranchForm
    success_url = ''

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
            profile_form = authUserForm()
            context = {'profile_form': profile_form}  
            return render(request, 'journal/login.html', context)


class TimetableView(View):

    def get(self,request,br_id=0,t_id=0):
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

        branchs = Branch.objects.all()
        form = AddTimetableForm()
        

#        tt = Timetable.objects.order_by('timetb','id_branch','day_of_week')
        if br_id:
            tt = Timetable.objects.filter(id_branch=br_id, active=True)
        else:
            tt = Timetable.objects.filter(active=True)
        for it in tt:
            # bbr = it.id_branch
            # if it.id_branch.title not in d[allweek.index(it.day_of_week)]['tt'].keys():
            #     d[allweek.index(it.day_of_week)]['tt'][it.id_branch.title] = []
            d[allweek.index(it.day_of_week)]['tt'].append(it)

        return render(request, 'journal/timetable.html', {'title':'Расписание', 'timetable':tt, 'branchs':branchs, 'd':d, 'form':form})

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
        active = Teacher.objects.filter(is_active=True).exclude(user_id=None)
        notactive = Teacher.objects.filter(is_active=False)
        new = Teacher.objects.filter(is_active=True, user_id=None)

        form = AddTeacherForm()

        return render(request,'journal/teacherlist.html', {'active': active, 
                                                           'notactive':notactive,
                                                           'new': new,
                                                           'form': form,
                                                           })
    

    def post(self, request):
        print(request)
        if request.POST['action'] == 'add':
            form = AddTeacherForm(request.POST)
            form.save()

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

        # br = User.objects.get(pk=1)
        # print(br)
        # d = {'id_teacher':br, 'last_sum':650}
        # Salary.objects.create(**d)

        user = request.user
        allwt = TeacherJournal.objects.filter(ispaid = False, id_teacher = user.id)
        form = AddWorkingTimeForm()
        
        return render(request,'journal/workingtime.html',{'journal': allwt, 'form':form})

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

        data = {}
        # список действующих работников
        teachers = Teacher.objects.filter(is_active=True)
        for teacher in teachers:
            data[teacher.id] ={'id': teacher.id, 'last_name': teacher.last_name, 'first_name': teacher.first_name, 'tt': []}
        # список неопл занятий
        wt = TeacherJournal.objects.filter(ispaid=False)
        for item in wt:
            r = Salary.objects.filter(date_of_activate__lte=item.date_of_visit, id_teacher=item.id_teacher).order_by('date_of_activate').last()
            item.last_sum = r.last_sum
            item.total = item.last_sum * item.number_hours
            data[item.id_teacher.id]['tt'].append(item)
        content = {
            'data': data.values(), # список преподов, сумма к выплате, + подсписок с расшифровкой
        }
        return render(request,'journal/salary.html', content)
    
    def post(self, request):
        data = json.load(request)
        print(data)
        res = list(map(int, data['lst']))
        print(res)
        TeacherJournal.objects.filter(pk__in=res).update(ispaid=True, date_of_paid=datetime.today())
        return JsonResponse({'res': res})
        

class TeacherPaidViev(View):
    def get(self,request):
        pass

class BookingView(View):
    def get(self,request,br_id,course):

    # из графика достать следующие варианты на всю неделю
        tt = Timetable.objects.filter(active=True)
        if br_id:
            tt = tt.filter(id_branch = br_id)
        if course:
            tt = tt.filter(id_course = course)

        #даты на ближайшую неделю
        week = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        wd = datetime.today().weekday()
        sweek = week[wd:]+week[:wd]
        dweek = dict()
        for id in range(len(sweek)):
            dweek[sweek[id]] = datetime.today()+timedelta(id)

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
        booking = visits.filter(date__gte=datetime.today()).filter(reserv=True)
        visits = visits.filter(date__lt=datetime.today()).values(
            'id_client__id',
            'id_client__name',
            'id_client__surname',
            'id_timetable_id__id_course__title',
            'id_timetable_id__id_branch__title',
            'id_timetable_id__timetb'
            ).annotate(total=Max('date'))
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
        
        # получить расписание только для текущего препода
        user = request.user
        teacher = Teacher.objects.get(user_id=user)

        tt = Timetable.objects.filter(active=True).filter(id_teacher = teacher)

        # найти все брони на эти расписания

        booking = VisitFix.objects.filter(reserv=True, visit=False, id_timetable__id_teacher=teacher).order_by('date')


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
            # bob.reserv = False
            # bob.save()

            # запустить бота, предупредить завуча
            # проверить оплаты:
            pay = Paying.objects.filter(id_client=bob.id_client, id_course=bob.id_timetable.id_course).last()
            # если ничего не оплачено, то игнор
            # если оплачен разовый сеанс,то игнор
            # если абонемент, то предупреждать
            if pay.subscription > 1 and pay.subscription > pay.used_lesson:
                pass

        return redirect(f'/visitors/{br_id}/{course}')


