## =============================================================================
## admin.py
## =============================================================================

from django.contrib import admin
from app.models.models import *

# Register your models here.
admin.site.register(Movie)
admin.site.register(Tweet)
