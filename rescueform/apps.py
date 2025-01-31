# rescueform/apps.py
from django.apps import AppConfig

class RescueformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rescueform'

    def ready(self):
        from .firebase import initialize_firebase
        initialize_firebase()  # Initialize Firebase when the app starts