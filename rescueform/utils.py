from firebase_admin import messaging, exceptions
from .models import FCMToken


def send_fcm_notification(user, title, body, url=None):
    try:
        # Check if user has push notifications enabled
        if hasattr(user, 'profile') and not user.profile.pushnoti:
            print(f"🔕 Notifications disabled for user {user}")
            return False

        # Get FCM token from database
        fcm_token = FCMToken.objects.get(user=user)
        token = fcm_token.token

        # Validate token first
        try:
            messaging.send(
                messaging.Message(token=token),
                dry_run=True
            )
        except exceptions.UnregisteredError:
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
        print(f"🚨 Error: {str(e)}")
        return False


def validate_fcm_token(user):
    """Check if a user's FCM token is valid"""
    try:
        fcm_token = FCMToken.objects.get(user=user)
        messaging.send(
            messaging.Message(token=fcm_token.token),
            dry_run=True
        )
        return True
    except (FCMToken.DoesNotExist, exceptions.UnregisteredError):
        return False
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return False


def delete_fcm_token(user):
    """Delete a user's FCM token"""
    try:
        FCMToken.objects.filter(user=user).delete()
        print(f"🗑️ Deleted FCM token for user {user}")
        return True
    except Exception as e:
        print(f"Error deleting token: {str(e)}")
        return False