from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RecommendationForm, ByTopicForm
from .models import Episodes
from .application import VespaApp
api_key_path = "/home/guilherme/.vespa/grupo5.api-key.pem"
app = VespaApp(key_location=api_key_path)

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
        if model in ["semantic","fusion","bm25"]:
            result = app.query(model,topic).to_html()

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
            result = app.query(model, Episodes.objects.get(pk=episode).transcript)[1:].to_html()
            return render(request,
                          "results.html",
                          {
                              "result": result
                          })
        else:
            return HttpResponse(f"Não podemos executar a busca no episódio {episode} para o modelo {model}")
