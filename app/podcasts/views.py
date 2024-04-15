from django.http import HttpResponse
from django.shortcuts import render, redirect

import pandas as pd

from .forms import RecommendationForm, ByTopicForm
from .models import Episodes
#from .application import VespaApp

#app = VespaApp()

def index(request):
    return render(request, "index.html")

def search_by_topic(request):
    model = request.GET.get("model")
    topic = request.GET.get("topic")
    if model is None or topic is None:
        form = ByTopicForm()
        return render(request,
                      "search_by_topic.html",
                      {
                          "form": form
                       })
    else:
        if model == "semantic":
            # result = app.query_semantic(Episodes.objects.get(pk=episode).transcript)
            return HttpResponse(f"model {model} for topic {topic}")
        elif model == "fusion":
            return HttpResponse(f"model {model} for topic {topic}")
        elif model == "bm25":
            return HttpResponse(f"model {model} for topic {topic}")
        else:
            return HttpResponse(f"The model {model} are not on of supported models")

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
            dummy_data = pd.DataFrame({
                "id": [35, 87],
                "title": ["Fall Cleareance Sales", "A Very Special Sedaris Christmas"]
            })
            #result = app.query_semantic(Episodes.objects.get(pk=episode).transcript)
            return HttpResponse(dummy_data.to_html())
        else:
            return HttpResponse(f"Não podemos executar a busca no episódio {episode} para o modelo {model}")
