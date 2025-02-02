import json
import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.views.decorators.http import require_POST
from user.models import Profile
from .firebase import initialize_firebase
import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import submission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import FCMToken

# Create your views here.
@login_required(login_url='/user/login/')
def form(request):
    try:
        initialize_firebase()
    except:
     int(1+1)
    return render(request,'form.html')

def index(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def toggle_mail_notifications(request):
    user_profile = request.user.profile
    # Toggle the mail notification setting
    user_profile.mailnoti = not user_profile.mailnoti
    user_profile.save()

    # Return the new state as JSON
    return JsonResponse({
        'status': 'success',
        'mailnoti': user_profile.mailnoti
    })

@require_POST
@login_required
def toggle_notifications(request):
    try:
        profile = request.user.profile
        profile.pushnoti = not profile.pushnoti
        profile.save()

        if not profile.pushnoti:
            # Optional: Delete FCM token when disabling
            request.user.fcmtoken.delete()

        return JsonResponse({
            'status': 'success',
            'pushnoti': profile.pushnoti
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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
        return "Unknown" if city else "Address not found"

@require_POST
@login_required
def delete_fcm_token(request):
    try:
        user = request.user
        FCMToken.objects.filter(user=user).delete()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.pushnoti = False
        profile.save()
        return JsonResponse({'status': 'success', 'message': 'Notifications disabled'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def save_fcm_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            user = request.user
            profile, created = Profile.objects.get_or_create(user=user)
            profile.pushnoti = True
            profile.save()
            FCMToken.objects.update_or_create(user=user, defaults={'token': token})
            print(f"Token saved for {user.username}: {token}")  # Check terminal logs
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print("Error saving token:", str(e))  # Debug errors
            return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
@require_POST
@login_required
def update_fcm_token(request):
    try:
        user = request.user
        new_token = request.POST.get('token')

        # Update or create the FCM token
        FCMToken.objects.update_or_create(
            user=user,
            defaults={'token': new_token}
        )
        return JsonResponse({'status': 'success', 'message': 'Token updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
def mail_noti(self):


    titles = [
        "🐾 A Little Friend Needs Help! 🐾",
        "🚨 Emergency: Animal in Distress! 🚨",
        "❤️🩹 A Furry Friend Needs You! ❤️🩹",
        "🐾 Help a Soul in Need! 🐾",
        "⚠️ Urgent: Animal Rescue Needed! ⚠️",
        "🐾 A Life is Waiting for You! 🐾",
        "❤️ A Precious Creature Needs Aid! ❤️",
        "🐾 Can You Be Their Hero? 🐾",
        "🚨 Quick! An Animal Needs Rescue! 🚨",
        "🐾 A Little Paw Needs Your Help! 🐾"
    ]
    bodies = [
        f"{random.choice(['😢', '🩹', '❤️🩹'])} {self.username} spotted an injured {self.animal  or 'animal'} nearby! "
        f"Can you check the details? Every minute matters...",
        f"A little {self.animal or 'creature'} is in trouble near {self.address}. "
        f"{random.choice(['Please lend a hand!', 'Your help could save a life!'])}",
        f"🚨 Emergency! A {self.animal  or 'helpless animal'} needs immediate assistance at {self.address}. "
        f"{random.choice(['Can you help?', 'Your kindness could save them!'])}",
        f"❤️ A {self.animal  or 'sweet soul'} is in pain near {self.address}. "
        f"{random.choice(['Can you be their hero?', 'Your action could make all the difference!'])}",
        f"🐾 A {self.animal  or 'little friend'} is hurt and needs your help at {self.address}. "
        f"{random.choice(['Please act quickly!', 'Every second counts!'])}",
        f"⚠️ Urgent! A {self.animal  or 'vulnerable animal'} needs rescue at {self.address}. "
        f"{random.choice(['Can you assist?', 'Your help could save a life!'])}",
        f"😢 A {self.animal  or 'poor creature'} is suffering near {self.address}. "
        f"{random.choice(['Can you lend a hand?', 'Your kindness could save them!'])}",
        f"🐾 A {self.animal  or 'little paw'} needs your help at {self.address}. "
        f"{random.choice(['Please act now!', 'Your action could save a life!'])}",
        f"❤️🩹 A {self.animal  or 'helpless animal'} is in distress near {self.address}. "
        f"{random.choice(['Can you help?', 'Your kindness could save them!'])}",
        f"🚨 Quick! A {self.animal  or 'little friend'} needs rescue at {self.address}. "
        f"{random.choice(['Can you assist?', 'Your help could save a life!'])}"
    ]

    from django.contrib.auth.models import User

    # Only send to users with FCM tokens
    users_with_tokens = User.objects.filter(

        profile__mailnoti=True
    ).distinct()
    for user in users_with_tokens:
        user.profile.pushnoti=True
        send_email(user.email, random.choice(titles), random.choice(bodies))


def send_email(recipient_email,title,body):
    smtp_server = "smtp.gmail.com"  # Example: Gmail SMTP server
    smtp_port = 587  # Port for TLS
    sender_email = os.environ.get("EMAIL_HOST_USER")
    mail_pass = os.environ.get("EMAIL_HOST_PASSWORD")
    # sender_email = logindetails.sender_email
    # mail_pass = logindetails.sender_password
    sub = title
    body = body
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = sub
    message.attach(MIMEText(body, "plain"))  # Attach the plain-text body to the message

    try:
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, mail_pass)  # Log in to the server
            server.send_message(message)  # Send the email
            print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

def push_noti(self):

    from .utils import send_fcm_notification
    titles = [
        "🐾 A Little Friend Needs Help! 🐾",
        "🚨 Emergency: Animal in Distress! 🚨",
        "❤️🩹 A Furry Friend Needs You! ❤️🩹",
        "🐾 Help a Soul in Need! 🐾",
        "⚠️ Urgent: Animal Rescue Needed! ⚠️",
        "🐾 A Life is Waiting for You! 🐾",
        "❤️ A Precious Creature Needs Aid! ❤️",
        "🐾 Can You Be Their Hero? 🐾",
        "🚨 Quick! An Animal Needs Rescue! 🚨",
        "🐾 A Little Paw Needs Your Help! 🐾"
    ]
    bodies = [
        f"{random.choice(['😢', '🩹', '❤️🩹'])} {self.username} spotted an injured {self.animal  or 'animal'} nearby! "
        f"Can you check the details? Every minute matters...",
        f"A little {self.animal or 'creature'} is in trouble near {self.address}. "
        f"{random.choice(['Please lend a hand!', 'Your help could save a life!'])}",
        f"🚨 Emergency! A {self.animal  or 'helpless animal'} needs immediate assistance at {self.address}. "
        f"{random.choice(['Can you help?', 'Your kindness could save them!'])}",
        f"❤️ A {self.animal  or 'sweet soul'} is in pain near {self.address}. "
        f"{random.choice(['Can you be their hero?', 'Your action could make all the difference!'])}",
        f"🐾 A {self.animal  or 'little friend'} is hurt and needs your help at {self.address}. "
        f"{random.choice(['Please act quickly!', 'Every second counts!'])}",
        f"⚠️ Urgent! A {self.animal  or 'vulnerable animal'} needs rescue at {self.address}. "
        f"{random.choice(['Can you assist?', 'Your help could save a life!'])}",
        f"😢 A {self.animal  or 'poor creature'} is suffering near {self.address}. "
        f"{random.choice(['Can you lend a hand?', 'Your kindness could save them!'])}",
        f"🐾 A {self.animal  or 'little paw'} needs your help at {self.address}. "
        f"{random.choice(['Please act now!', 'Your action could save a life!'])}",
        f"❤️🩹 A {self.animal  or 'helpless animal'} is in distress near {self.address}. "
        f"{random.choice(['Can you help?', 'Your kindness could save them!'])}",
        f"🚨 Quick! A {self.animal  or 'little friend'} needs rescue at {self.address}. "
        f"{random.choice(['Can you assist?', 'Your help could save a life!'])}"
    ]

    from django.contrib.auth.models import User

    # Only send to users with FCM tokens
    users_with_tokens = User.objects.filter(
        fcmtoken__isnull=False,
        profile__pushnoti=True
    ).distinct()
    for user in users_with_tokens:

        send_fcm_notification(
            user=user,
            title=random.choice(titles),
            body=random.choice(bodies),
            url=f"/dashboard/{self.id}/"
        )

@login_required(login_url='/user/login/')
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
        try:
            push_noti(self=subm)
        except Exception as e:
            print(e)


        return redirect('/dashboard/')


@login_required(login_url='/user/login/')
def my_reports(request):
    # return render(request, "reportDashboard.html", {})
    submissions =  submission.objects.filter(username=request.user.username).order_by("-id")

    subs = submission.objects.filter(latitude__isnull=False, longitude__isnull=False)
    location_data=[{'latitude':sub.latitude,'longitude':sub.longitude} for sub in subs]
    return render(request, 'reportDashboard.html', {'usersubm': submissions,'storedReports': submission.objects.all().order_by("-id"), 'location_data': location_data})

@login_required(login_url='/user/login/')
def emergency_report_list(request):
    if request.user.is_superuser or request.user.groups.filter(name='supervisor').exists():
        reports = submission.objects.all()
        return render(request, 'sup_reports.html', {'reports': reports.order_by("-id")})
    else:
        return HttpResponseForbidden()


login_required(login_url='user/login/')
def update_status(request, report_id):
    if request.user.is_superuser or request.user.groups.filter(name='supervisor').exists():
        if request.method == "POST":
            report = get_object_or_404(submission, id=report_id)
            report.status = request.POST.get('status')
            report.save()
        return redirect('emergency_report_list')
    else:
        return HttpResponseForbidden()

login_required(login_url='user/login/')
def delete_report(request, report_id):
    if request.user.is_superuser or request.user.groups.filter(name='supervisor').exists():
        if request.method == "POST":
            report = get_object_or_404(submission, id=report_id)
            report.delete()
        return redirect('emergency_report_list')
    else:
        return HttpResponseForbidden()

login_required(login_url='user/login/')
def reportdetails(request, report_id):
    report = get_object_or_404(submission, id=report_id)
    return render(request, 'reportdetails.html', {'report': report})


