## =============================================================================
## urls.py
## =============================================================================

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index', views.index, name='index'),
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^results', views.get_results_page, name='results'),
    url(r'^get_data', views.results, name='get_data'),
]
