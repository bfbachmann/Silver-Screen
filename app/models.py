from django.db import models
from django import forms

class QueryForm(forms.Form):
    query = forms.CharField(label='Movie Title', max_length=100)
