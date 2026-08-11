from django.contrib import admin

# Dashboard app doesn't need its own admin as it uses other apps' models
# But we can register it for completeness
from django.apps import apps

# Register models from other apps for admin dashboard
# This is optional as these are already registered in their respective apps