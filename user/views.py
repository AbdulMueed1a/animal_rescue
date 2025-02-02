import os

from django.db.models.signals import post_save

from .models import Profile
from rescueform.models import FCMToken
from django.dispatch import receiver
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from credentials import logindetails
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request,'user.html')

def generate_otp(length=6):
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

def send_email(note,recipient_email):
    smtp_server = "smtp.gmail.com"  # Example: Gmail SMTP server
    smtp_port = 587  # Port for TLS
    sender_email = os.environ.get("EMAIL_HOST_USER")
    mail_pass = os.environ.get("EMAIL_HOST_PASSWORD")
    # sender_email = logindetails.sender_email
    # mail_pass = logindetails.sender_password
    sub = "Your One-Time Password (OTP)"
    body = f"""
               This is your One-Time Password (OTP): {note}. Use it now to proceed with your request.

        Unlike typical OTPs, this one has no expiration, but don’t take this as an excuse to delay. Act promptly.

        If you didn’t request this OTP or suspect any unauthorized activity, you must contact our support team immediately at {sender_email}. Neglecting this could put your account's security at risk. 
          """
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

def register(request):
    if request.method == 'POST':
        # Use .get() to avoid MultiValueDictKeyError
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        mnoti = request.POST.get('mailnoti', 'false')  # checkboxes might not be in POST if unchecked
        pnoti = request.POST.get('pushnoti', 'false')

        # Optionally, check if required fields are provided:
        if not first_name or not last_name or not email or not username:
            messages.error(request, "All fields are required!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('signup')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already registered')
            return redirect('signup')

        # Generate OTP and send email
        otp = generate_otp()
        send_email(otp, email)

        # Save user data temporarily in the session
        request.session['user_data'] = {
            'username': username,
            'email': email,
            'password': password1,
            'first_name': first_name,
            'last_name': last_name,
            'otp': otp,
            'mailnoti': mnoti,
            'pushnoti': pnoti
        }
        return render(request, "otpenter.html", {'email': email})

    return render(request, "signup.html")

def otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        user_data = request.session.get('user_data')

        if not user_data:
            messages.error(request, 'Session expired. Please try again.')
            return redirect('signup')

        if entered_otp == user_data['otp']:
            # OTP is correct, create the user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )

            # Convert checkbox string values to booleans
            mail_noti_bool = user_data.get('mailnoti', '').lower() in ['true', 'on']
            push_noti_bool = user_data.get('pushnoti', '').lower() in ['true', 'on']

            # Retrieve FCM token
            fcm_token = request.POST.get('fcm_token', '')

            # Store notification preferences in the profile (if applicable)
            profile = user.profile
            profile.mailnoti = mail_noti_bool
            profile.pushnoti = push_noti_bool
            profile.save()

            # Save FCM token only if push notifications are enabled
            if push_noti_bool and fcm_token:
                FCMToken.objects.create(user=user, token=fcm_token)

            messages.success(request, 'Registration successful!')
            del request.session['user_data']  # Clear session data
            return redirect('login')

        else:
            messages.error(request, 'Incorrect OTP. Please try again.')
            return redirect('otp')

    return render(request, "otpenter.html")



def login(request):
    if request.user.is_authenticated:
        redirect('logout/')
    if request.method == 'POST':
        username = request.POST['Email_username']
        password = request.POST['password']

        if '@' in username:
            user = auth.authenticate(email=username, password=password)
        else:
            user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            next_url = request.GET.get("next", "/")  # Default to `/` if `next` is not provided
            return redirect(next_url)
        else:
            # Authentication failed, show an error message
            messages.error(request, "Invalid username/email or password.")
            return render(request, "login.html", {'error': 'Invalid credentials'})

    else:
        return render(request, "login.html")

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('/..')
    else:
        return redirect('/user/login')
