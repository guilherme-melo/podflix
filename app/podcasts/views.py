from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RecommendationForm
from .models import Episodes
from .application import VespaApp

app = VespaApp()

def index(request):
    return render(request, "index.html")

def search_by_topic(request):
    return render(request, "search_by_topic.html")

def recommendation(request):
    model = request.GET.get("model")
    episode = request.GET.get("episode")
    if model is None or episode is None:
        form = RecommendationForm()
        return render(request,
                      "recommendation.html",
                      {
                          "form": form
                      })
    else:
        if model == "semantic":
            result = app.query_semantic(Episodes.objects.get(pk=episode).transcript)
            return HttpResponse(str(result))
        else:
            return HttpResponse(f"Não podemos executar a busca no episódio {episode} para o modelo {model}")
