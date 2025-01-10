from django.urls import path
from . import views

urlpatterns = [

    # path('my_reports', views.my_reports, name='my_reports'),
    path('form', views.form , name='form'),
    path('', views.index , name='home'),
    path('rescue_submit', views.rescue_submit , name='submit'),
    path('dasboard/', views.my_reports ),
]
