from django.http import HttpResponse
from django.shortcuts import render

from .models import Episodes

def index(request):
    return render(request, "index.html")

def search_by_topic(request):
    return render(request, "search_by_topic.html")

def recommendation(request):
    return render(request, "recommendation.html", {"episodes" : Episodes.objects.all()})