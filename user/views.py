import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.shortcuts import render, redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from credentials import logindetails

# Create your views here.
def index(request):
    return render(request,'user.html')

def generate_otp(length=6):
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp


def send_email(note,recipient_email):
    smtp_server = "smtp.gmail.com"  # Example: Gmail SMTP server
    smtp_port = 587  # Port for TLS
    sender_email = logindetails.sender_email
    mail_pass = logindetails.sender_password
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
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('signup')

        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        username = request.POST['username']
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
            'otp': otp
        }
        return render(request, "otpenter.html", {'email': email})

    return render(request, "signup.html")


def otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
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
            messages.success(request, 'Registration successful!')
            del request.session['user_data']  # Clear session data
            return redirect('login')  # Redirect to login or desired page
        else:
            messages.error(request, 'Incorrect OTP. Please try again.')
            return redirect('otp')

    return render(request, "otpenter.html")


def login(request):
    if request.method == 'POST':
        username=request.POST['Email_username']
        password=request.POST['password']

        if '@' in username:
            user = auth.authenticate(email=username, password=password)
        else:
            user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/user')

    else:
        return render(request,"login.html")

def logout(request):
    auth.logout(request)
    return redirect('/user')