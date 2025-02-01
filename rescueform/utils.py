# utils.py
from firebase_admin import messaging, exceptions

from rescueform.models import FCMToken


def send_fcm_notification(user, title, body, url=None):
    try:
        # Get FCM token from database
        fcm_token = FCMToken.objects.get(user=user)
        token = fcm_token.token

        # Validate token first
        try:
            # Test if token is valid
            messaging.send(
                messaging.Message(token=token),
                dry_run=True
            )
        except exceptions.UnregisteredError:
            # Token is invalid, delete it and return
            print(f"❌ Invalid token for user {user}, deleting...")
            fcm_token.delete()
            return False
        except exceptions.InvalidArgumentError:
            print(f"❌ Invalid token format for user {user}, deleting...")
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
        print(f"🚨 Unexpected error: {str(e)}")
        return False