from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from textblob import TextBlob
from difflib import SequenceMatcher

# Sample to-do list with additional metadata
# todo_list = [
#     {"task": "Read a book", "tags": ["relaxing", "entertainment"], "time": 60, "energy": "low"},
#     {"task": "Write a blog post", "tags": ["creative", "productive"], "time": 90, "energy": "medium"},
#     {"task": "Clean the house", "tags": ["tidying", "productive"], "time": 120, "energy": "high"},
#     {"task": "Meditate", "tags": ["relaxing", "comforting"], "time": 20, "energy": "low"},
#     {"task": "Cook a new recipe", "tags": ["creative", "entertainment"], "time": 45, "energy": "medium"},
#     {"task": "Do yoga", "tags": ["physical", "health"], "time": 30, "energy": "high"},
#     {"task": "Plan the week ahead", "tags": ["planning", "productive"], "time": 60, "energy": "medium"},
#     {"task": "Listen to a podcast", "tags": ["entertainment", "relaxing"], "time": 40, "energy": "low"},
# ]

# Predefined mood categories with associated tags
mood_categories = {
    "happy": ["fun", "joy", "relaxing", "social"],
    "sad": ["calm", "reflective", "quiet"],
    "angry": ["physical", "outlet", "productive"],
    "focused": ["work", "study", "concentration"],
    "relaxed": ["easy", "simple", "peaceful"]
}

# Helper functions
def match_mood(user_mood):
    best_match = None
    highest_similarity = 0
    for mood, tags in mood_categories.items():
        similarity = SequenceMatcher(None, user_mood, mood).ratio()
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = mood
    return best_match

def score_task(task, matched_mood, user_energy, max_time):
    tag_match = len(set(task["tags"]) & set(mood_categories[matched_mood]))

    blob = TextBlob(task["task"])
    sentiment_score = blob.sentiment.polarity

    energy_match = 1 if task["energy"] == user_energy else 0

    time_match = 1 if task["time"] <= max_time else 0

    return tag_match * 2 + sentiment_score + energy_match + time_match

def filter_and_rank_tasks(todo_list, user_mood, user_energy, max_time):
    matched_mood = match_mood(user_mood)
    if not matched_mood:
        return []

    scored_tasks = []
    for task in todo_list:
        score = score_task(task, matched_mood, user_energy, max_time)
        scored_tasks.append({"task": task["task"], "score": score})

    # Sort by score in descending order
    scored_tasks.sort(key=lambda x: x["score"], reverse=True)
    return [task["task"] for task in scored_tasks if task["score"] > 0]

# Serializer class
class MoodAnalyseSerializer(serializers.Serializer):
    mood = serializers.CharField(required=True)
    energy = serializers.ChoiceField(choices=["low", "medium", "high"], required=True)
    time = serializers.IntegerField(min_value=0, required=True)
    tasks = serializers.ListField(child=serializers.DictField(), required=True)
# API View class
class MoodAnalyseView(APIView):
    def get(self, request):
        return Response({"status": "success", "message": "Welcome to the Mood Analyser API!"}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = MoodAnalyseSerializer(data=request.data)
        if serializer.is_valid():
            user_mood = serializer.validated_data["mood"].strip().lower()
            user_energy = serializer.validated_data["energy"].strip().lower()
            max_time = serializer.validated_data["time"]
            todo_list = serializer.validated_data["tasks"]
            filtered_tasks = filter_and_rank_tasks(todo_list, user_mood, user_energy, max_time)

            if filtered_tasks:
                return Response({"status": "success", "tasks": filtered_tasks}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "error", "message": "No tasks found for the given mood.", "tasks": []}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# urls.py
# from django.urls import path
# from .views import MoodAnalyseView

# urlpatterns = [
#     path('mood_analyse/', MoodAnalyseView.as_view(), name='mood_analyse'),
# ]
