from django.contrib import admin
from .models import FCMToken  # Import your model

@admin.register(FCMToken)  # Register the model
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')