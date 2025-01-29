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
from django.contrib.auth.models import User

# Create your views here.
def form(request):
    # if request.user.is_authenticated:
        return render(request,'form.html')
    # else:
    #     return redirect('../user/login')
def index(request):
    return render(request, 'index.html')


import requests


def reverse_geocode(lat, lon, city=False):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "accept-language": "en"  # Ensure English output
    }
    headers = {
        "User-Agent": "ANIMAL_RESCUE_PORTAL/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if city:
            # Try different fields commonly used for city names
            return (
                    data.get("address", {}).get("city") or
                    data.get("address", {}).get("town") or
                    data.get("address", {}).get("village") or
                    data.get("address", {}).get("hamlet") or
                    data.get("address", {}).get("county") or  # Sometimes used in Pakistan
                    data.get("address", {}).get("state_district") or
                    "Unknown"
            )

        return data.get("display_name", "Address not found")

    except requests.RequestException as e:
        print("Error during reverse geocoding:", e)
        return "Unknown" if city else "Address not found"


# @login_required(login_url='/login/')
def rescue_submit(request):
    subm = submission()
    if request.method == "POST":
        user = User.objects.get(username=request.user.username)
        subm.username = request.user.username
        subm.name = user.first_name + " " + user.last_name
        subm.email = user.email
        subm.animal = request.POST['animal']
        subm.contact = request.POST['contact']
        subm.image = request.FILES['image']
        if request.POST['date']:
            subm.date = request.POST['date']

        radio = request.POST.get('location_type')
        print("Reverse geocode result:", reverse_geocode(subm.latitude, subm.longitude, city=True))

        if radio == 'manual':
            subm.city = request.POST['city'] if request.POST.get('city') else 'Unknown'
            subm.address = request.POST['address']
        elif radio == 'map':
            subm.latitude = request.POST['latitude']
            subm.longitude = request.POST['longitude']
            subm.address = reverse_geocode(subm.latitude, subm.longitude)
            subm.city = reverse_geocode(subm.latitude, subm.longitude, city=True)

        # Ensure city is set
        if not subm.city:
            subm.city = 'Unknown'  # or raise an error

        print(subm.address)
        subm.condition = request.POST['condition']
        subm.description = request.POST['description']

        subm.save()
        image_path = subm.image.path
        return redirect('dashboard/')


@login_required(login_url='/login/')
def my_reports(request):
    # return render(request, "reportDashboard.html", {})
    submissions =  submission.objects.filter(username=request.user.username).order_by("-id")

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
