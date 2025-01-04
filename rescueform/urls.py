from django.urls import path
from . import views

urlpatterns = [
    path('', views.form , name='form'),
    path('rescue_submit', views.rescue_submit , name='submit'),
]
