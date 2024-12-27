

from django.urls import path
from .views import MoodAnalyseView
urlpatterns = [
    path('mood_analyse/', MoodAnalyseView.as_view(), name='mood-analyse')
]
