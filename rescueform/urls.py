from django.urls import path
from . import views

urlpatterns = [

    # path('my_reports', views.my_reports, name='my_reports'),
    path('reports/', views.emergency_report_list, name='emergency_report_list'),
    path('reports/update/<int:report_id>/', views.update_status, name='update_status'),
    path('reports/delete/<int:report_id>/', views.delete_report, name='delete_report'),
    path('form', views.form , name='form'),
    path('', views.index , name='home'),
    path('rescue_submit', views.rescue_submit , name='submit'),
    path('dashboard/', views.my_reports ),
]
