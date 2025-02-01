from django.urls import path
from . import views


urlpatterns = [

    # path('my_reports', views.my_reports, name='my_reports'),
    path('reports/', views.emergency_report_list, name='emergency_report_list'),
    path('reports/update/<int:report_id>/', views.update_status, name='update_status'),
    path('reports/delete/<int:report_id>/', views.delete_report, name='delete_report'),
    path('dashboard/', views.my_reports ),
    path('dashboard/<int:report_id>/', views.reportdetails, name='details'),
    path('form/', views.form , name='form'),
    path('', views.index , name='home'),
    path('rescue_submit/', views.rescue_submit , name='submit'),
    path('aboutus/', views.aboutus , name='aboutus' ),
    path('save-fcm-token/', views.save_fcm_token, name='save_fcm_token'),
    path('toggle-notifications/', views.toggle_notifications, name='toggle_notifications'),
    path('delete-fcm-token/', views.delete_fcm_token, name='delete_fcm_token'),
    path('update-fcm-token/', views.update_fcm_token, name='update_fcm_token')
]
