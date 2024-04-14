from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index.html", views.index, name="index"),
    path("search_by_topic.html", views.search_by_topic, name="search_by_topic"),
    path("recommendation.html", views.recommendation, name="recommendation")
]