"""
REST API endpoints — for using Feel Comfort LLM from external projects.
Base URL: /api/

Other projects can call these endpoints to use the same Groq/Ollama LLM.

Example:
  POST /api/analyze/
  Headers: Authorization: Bearer <api_token>
  Body: {"text": "I feel so anxious today", "user_id": "user123"}
  Response: {"mood": "anxious", "response": "...", "activities": [...]}
"""

from django.urls import path
from . import api_views

urlpatterns = [
    path('analyze/',  api_views.analyze_mood_api,  name='api_analyze'),
    path('history/',  api_views.history_api,        name='api_history'),
    path('health/',   api_views.health_check,       name='api_health'),
]
