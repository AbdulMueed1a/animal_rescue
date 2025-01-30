
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rescueform'

    def ready(self):
        from rescueform.firebase import initialize_firebase
        initialize_firebase()

class AnimalreascueProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Animalrescue_project'
