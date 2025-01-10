import os
import time

from django.shortcuts import render, redirect

import user
from .models import submission
# Create your views here.
def form(request):
    if request.user.is_authenticated:
        return render(request,'form.html')
    else:
        return redirect('../user/login')
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
        return redirect('dasboard/')

def my_reports(request):
    # return render(request, "reportDashboard.html", {})

    if request.user.is_authenticated:
        submissions = submission.objects.filter(email=request.user.email)
        return render(request, 'reportDashboard.html', {'usersubm': submissions,'storedReports': submission.objects.all()})
    else:
        return redirect('../user/login')
