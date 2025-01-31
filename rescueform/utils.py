# rescueform/utils.py
from django.contrib.auth import get_user_model
from django.apps import apps
from firebase_admin import messaging
from .models import FCMToken


def send_fcm_notification(user, title, body, url=None):
    try:
        # Get FCM token from database
        fcm_token = FCMToken.objects.get(user=user)
        token = fcm_token.token

        # Validate token first
        try:
            messaging.send(
                messaging.Message(token=token),
                dry_run=True
            )
        except Exception as e:
            print(f"❌ Invalid token for user {user}, deleting...")
            fcm_token.delete()
            return False

        # Build message with data payload
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
            data={'url': url} if url else {}
        )

        # Send notification
        response = messaging.send(message)
        print(f"✅ Notification sent: {response}")
        return True

    except FCMToken.DoesNotExist:
        print(f"❌ No FCM token found for user {user}")
        return False
    except Exception as e:
        print(f"🚨 Error: {str(e)}")
        return False