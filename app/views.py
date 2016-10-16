from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import QueryForm

# Render the front page of the website with the query form
# TODO: upadte this once we have analysis working
def index(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        query_form = QueryForm(request.POST)

        # check whether it's valid:
        if query_form.is_valid():
            # redirect to a new URL:
            return render(request, 'results.html', {'form': query_form})

     # if a GET (or any other method) we'll create a blank form
    else:
        query_form = QueryForm()

    return render(request, 'index.html', {'form': query_form})

def results(request):
    if request.method == 'POST':
        return render(request, 'results.html', {'form': QueryForm(request.POST)})
    else:
        return HttpResponseRedirect('/index/')
