## =============================================================================
## urls.py
## =============================================================================

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index', views.index, name='index'),
    url(r'^$', views.index, name='index'),
    url(r'^results', views.results, name='results'),
]
