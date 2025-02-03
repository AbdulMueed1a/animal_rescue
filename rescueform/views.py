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
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
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

@require_POST
@login_required
def toggle_mail_notifications(request):
    try:
        enabled = json.loads(request.body).get('enabled', False)
        request.user.profile.mailnoti = enabled
        request.user.profile.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def service_worker(request):
    return HttpResponse(
        open('static/firebase-messaging-sw.js').read(),
        content_type='application/javascript'
    )

@require_POST
@login_required
def toggle_push_notifications(request):
    try:
        enabled = json.loads(request.body).get('enabled', False)
        request.user.profile.pushnoti = enabled
        request.user.profile.save()
        return JsonResponse({'status': 'success'})
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
    if request.method == "POST":
        try:
            subm = submission()
            user = request.user  # Directly use the authenticated user

            # Basic user info
            subm.username = user.username
            subm.name = f"{user.first_name} {user.last_name}"
            subm.email = user.email

            # Animal and contact info
            subm.animal = request.POST['animal']
            subm.contact = request.POST['contact']

            # Image handling with Cloudinary
            # image_file = request.FILES.get('image')
            subm.image = request.FILES.get('image')
            # if image_file:
            #     # Upload to Cloudinary with error handling
            #     result = cloudinary.uploader.upload(
            #         image_file,
            #         folder="rescue_submissions/",
            #         resource_type="image",
            #         allowed_formats=['jpg', 'png', 'jpeg']
            #     )
            #     subm.image_url = result['secure_url']  # Store Cloudinary URL

            # Date handling
            if request.POST.get('date'):
                subm.date = request.POST['date']

            # Location handling
            location_type = request.POST.get('location_type')
            if location_type == 'manual':
                subm.city = request.POST.get('city', 'Unknown')
                subm.address = request.POST.get('address', '')
            elif location_type == 'map':
                subm.latitude = request.POST.get('latitude')
                subm.longitude = request.POST.get('longitude')
                try:
                    subm.address = reverse_geocode(subm.latitude, subm.longitude)
                    subm.city = reverse_geocode(subm.latitude, subm.longitude, city=True)
                except Exception as geocode_error:
                    print(f"Geocoding failed: {geocode_error}")
                    subm.city = 'Unknown'

            # Description and condition
            subm.condition = request.POST.get('condition', '')
            subm.description = request.POST.get('description', '')

            # Save and send notifications
            subm.save()

            try:
                push_noti(subm)  # Your existing notification function
            except Exception as noti_error:
                print(f"Notification failed: {noti_error}")

            return redirect('/dashboard/')

        except KeyError as ke:
            print(f"Missing form field: {ke}")
            return redirect('/error/missing-fields/')

        except Exception as e:
            print(f"Submission error: {e}")
            return redirect('/error/generic/')

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

def missing_fields_error(request):
    return render(request, 'errors/missing_fields.html', status=400)

def generic_error(request):
    return render(request, 'errors/generic.html', status=500)

