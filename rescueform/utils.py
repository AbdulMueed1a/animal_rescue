# utils.py
# utils.py
from firebase_admin import messaging
from .models import FCMToken

def send_fcm_notification(user, title, body, url=None):
    try:
        token = FCMToken.objects.get(user=user).token
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
            data={"url": url} if url else {}
        )
        response = messaging.send(message)
        print(f"✅ Notification sent to {user.username}. Message ID: {response}")
    except FCMToken.DoesNotExist:
        print(f"❌ User {user.username} has no FCM token.")
    except Exception as e:
        print(f"❌ FCM error: {str(e)}")