import os
import time
from contextlib import nullcontext

from django.db.models import Q

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from itertools import chain
import requests
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



def reverse_geocode(lat, lon):

    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }
    headers = {
        "User-Agent": "YourAppName/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('display_name', "Address not found")
    except requests.RequestException as e:
        return f"Error: {e}"


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
        if request.POST['date']:
            subm.date = request.POST['date']
        if request.POST['address']:
            subm.address = request.POST['address']
        else:
            subm.latitude = request.POST['latitude']
            subm.longitude = request.POST['longitude']
            subm.address = reverse_geocode(subm.latitude, subm.longitude)
        print(subm.address)
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
    submissions.sort(key=lambda x: x.id, reverse=True)
    subs = submission.objects.filter(latitude__isnull=False, longitude__isnull=False)
    location_data=[{'latitude':sub.latitude,'longitude':sub.longitude} for sub in subs]
    return render(request, 'reportDashboard.html', {'usersubm': submissions,'storedReports': submission.objects.all().order_by("-id"), 'location_data': location_data})

@login_required(login_url='/login/')
def emergency_report_list(request):
    # if request.user.is_authenticated and request.user.is_superuser:
        reports = submission.objects.all()
        return render(request, 'sup_reports.html', {'reports': reports.order_by("-id")})
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
