import os
import time

from django.shortcuts import render
from .models import submission
# Create your views here.
def form(request):
    return render(request,'form.html')
def index(request):
    return render(request, 'index.html')


def rescue_submit(request):
    subm = submission()
    if request.method == "POST":
        subm.name = request.POST['name']
        subm.email = request.POST['email']
        subm.contact = request.POST['contact']
        subm.province = request.POST['province']
        subm.image = request.FILES['image']
        subm.city = request.POST['city']
        subm.location = request.POST['location']
        subm.condition = request.POST['condition']
        subm.description = request.POST['description']
        subm.save()
        image_path = subm.image.path

        # time.sleep(5)
        return render(request,'submitted.html',{'subm':subm})

