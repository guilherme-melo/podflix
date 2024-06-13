from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RecommendationForm, ByTopicForm
from .models import Episodes
from .application import VespaApp
app = VespaApp()
print("here")

def index(request):
    return render(request, "index.html")

def search_by_topic(request):
    model = request.GET.get("model")
    topic = request.GET.get("topic")
    mv = request.GET.get("mv")
    if model is None or topic is None:
        form = ByTopicForm()
        return render(request,
                      "search_by_topic.html",
                      {
                          "form": form
                       })
    else:
        if model in ["semantic","fusion","bm25"]:
            result = app.query(input_query=topic, type_query=model, MV=mv).to_html()
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
    mv = request.GET.get("mv")
    input = request.GET.get("input")
    data = None
    if model is None or episode is None:
        form = RecommendationForm()
        return render(request,
                      "recommendation.html",
                      {
                          "form": form
                      })
    else:
        if input=="transcript":
            data = Episodes.objects.get(pk=episode).transcript
        elif input=="title":
            data = Episodes.objects.get(pk=episode).title
        elif input=="desc":
            data = Episodes.objects.get(pk=episode).description

        if model == "semantic":
            result = app.query(input_query=data, type_query=model, MV=mv).to_html()
            return render(request,
                          "results.html",
                          {
                              "result": result
                          })
        else:
            return HttpResponse(f"Não podemos executar a busca no episódio {episode} para o modelo {model}")
