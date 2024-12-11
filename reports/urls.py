from django.urls import path

from reports.views import *

urlpatterns = [
    path('get-all-weakly/', GetAllWeeklyReport.as_view(), name='get-all-weakly'),
    path('get-all-monthly/', GetAllMonthlyReport.as_view(), name='get-all-monthly'),
    path('<uuid:pk>/', GetDetailReport.as_view(), name='get-detail'),
]
