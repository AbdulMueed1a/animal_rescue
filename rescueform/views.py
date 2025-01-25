import os
import time

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from itertools import chain
import user
from .models import submission
from django.contrib.auth.decorators import login_required



# Create your views here.
def form(request):
    if request.user.is_authenticated:
        return render(request,'form.html')
    else:
        return redirect('../user/login')
def index(request):
    return render(request, 'index.html')

@login_required(login_url='/login/')
def rescue_submit(request):
    subm = submission()
    if request.method == "POST":
        subm.username = request.user.username
        subm.name = request.POST['name']
        subm.email = request.POST['email']
        subm.animal = request.POST['animal']
        subm.contact = request.POST['contact']
        subm.province = request.POST['district']
        subm.image = request.FILES['image']
        subm.city = request.POST['city']
        subm.date = request.POST['date']
        subm.location = request.POST['location']
        subm.condition = request.POST['condition']
        subm.description = request.POST['description']
        subm.save()
        image_path = subm.image.path
        # time.sleep(5)
        return redirect('dasboard/')


@login_required(login_url='/login/')
def my_reports(request):
    # return render(request, "reportDashboard.html", {})
    submissions = list(chain(submission.objects.filter(email=request.user.email) , submission.objects.filter(username=request.user.username)))
    return render(request, 'reportDashboard.html', {'usersubm': submissions,'storedReports': submission.objects.all()})

@login_required(login_url='/login/')
def emergency_report_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        reports = submission.objects.all()
        return render(request, 'sup_reports.html', {'reports': reports})
    # elif request.user.is_authenticated and not request.user.is_superuser:
    #     return HttpResponseForbidden()


login_required(login_url='/login/')
def update_status(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(submission, id=report_id)
        report.status = request.POST.get('status')
        report.save()
    return redirect('emergency_report_list')

login_required(login_url='/login/')
def delete_report(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(submission, id=report_id)
        report.delete()
    return redirect('emergency_report_list')
