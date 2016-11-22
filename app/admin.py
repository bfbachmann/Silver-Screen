## =============================================================================
## admin.py
## =============================================================================

from django.contrib import admin
from app.models.models import *

admin.site.register(Movie)
admin.site.register(Tweet)
admin.site.register(Sentiment)
