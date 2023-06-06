from django.contrib import admin

from .models import *

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('id_teacher', 'id_course', 'id_branch', 'day_of_week', 'timetb', 'duration')
    #list_display_links = ['id_teacher', 'id_course', 'id_branch']
    #search_fields = ('id_teacher', 'id_course', 'id_branch')
    list_filter = ('id_teacher', 'id_course', 'id_branch')


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name','contact','tg_name','is_active')


class SalaryAdmin(admin.ModelAdmin):
    list_display = ('id_teacher', 'last_sum','date_of_change')


class TeacherJournalAdmin(admin.ModelAdmin):
    list_display = ('id_teacher', 'id_course','id_branch','date_of_visit','number_hours','date_of_paid','ispaid')
    list_filter = ('id_teacher', 'ispaid')


class PayingAdmin(admin.ModelAdmin):
    list_display = ('id_client', 'id_course','id_branch','date','summ','subscription')
    list_filter = ('id_course', 'id_branch')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name','guardian','mobile_phone','active')
    list_filter = ('active','address')


class VisitFixAdmin(admin.ModelAdmin):
    list_display = ('id_client', 'id_timetable','date','visit')


admin.site.register(Teacher,TeacherAdmin)
admin.site.register(Course)
admin.site.register(Branch)
admin.site.register(Client,ClientAdmin)
admin.site.register(Salary,SalaryAdmin)
admin.site.register(TeacherJournal,TeacherJournalAdmin)
admin.site.register(Paying,PayingAdmin)
admin.site.register(VisitFix,VisitFixAdmin)

