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
        result = pd.DataFrame({
            "id": [35, 87],
            "title": ["Fall Cleareance Sales", "A Very Special Sedaris Christmas"]
        }).to_html()
        if model == "semantic":
            pass
            # result = app.query_semantic(topic).to_html()
        elif model == "fusion":
            pass
            # result = app.query_fusion(topic).to_html()
        elif model == "bm25":
            pass
            # result = app.query_bm25(topic).to_html()
        else:
            return HttpResponse(f"The model {model} are not on of supported models")
        return render(request,
                      "results.html",
                      {
                          "result": result
                      })


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
            return render(request,
                          "results.html",
                          {
                              "result": dummy_data.to_html()
                          })
        else:
            return HttpResponse(f"Não podemos executar a busca no episódio {episode} para o modelo {model}")
