from django.urls import include, path
from .views import *


urlpatterns = [
    # path('register/', registerPage, name='register'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('change_name/', registerNamePage, name='changeName'),
    
    # path('', LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TimetableView.as_view(), name='timetable'),
    path('filial/<int:br_id>/', TimetableView.as_view(), name='brtimetable'),
    path('filial/', BranchView.as_view(), name='branch'),
    path('course/', CourseView.as_view(), name='course'),
    path('client/', ClientView.as_view(), name='client'),
    path('teachers/', TeacherView.as_view(), name='teacherlist'),
    path('workingtime/', WorkingTimeView.as_view(), name='workingtime'),
    path('addworkingtime/', AddWorkingTimeView.as_view(), name='additem'),
    path('<int:pk>/delete', DellWorkingTimeView.as_view(), name='journal-delete'),
    path('visitors/<int:br_id>/<int:course>', VisitorsView.as_view(),name='visitors'),
    path('booking/<int:br_id>/<int:course>', BookingView.as_view(),name='booking'),
    path('workingtime/paying', TeacherSizePaidViev.as_view(),name='paying'),
    # path('salary', , name='salary')
]