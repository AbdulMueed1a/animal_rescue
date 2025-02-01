from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.register , name='signup'),
    path('otp', views.otp , name='otp'),
    path('login/', views.login , name='login'),
    path('logout/', views.logout , name='logout'),
]
