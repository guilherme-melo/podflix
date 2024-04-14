from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("search_by_topic", views.search_by_topic, name="search_by_topic"),
    path("recommendation", views.recommendation, name="recommendation"),
]