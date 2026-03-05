"""
REST API Views — allows MULTIPLE external projects to use
Feel Comfort's NLP + LLM backend via simple HTTP requests.

Authentication: Token-based (set API_SECRET_TOKEN in .env)
"""

import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .mood_analyzer import MoodAnalyzer
from .llm_handler import LLMHandler

_analyzer = MoodAnalyzer()
_llm      = LLMHandler()

API_TOKEN = os.getenv('API_SECRET_TOKEN', 'change-this-secret-token')


def _verify_token(request) -> bool:
    """Simple token auth for API access"""
    auth = request.headers.get('Authorization', '')
    return auth == f'Bearer {API_TOKEN}'


@csrf_exempt
@require_POST
def analyze_mood_api(request):
    """
    POST /api/analyze/
    Headers: Authorization: Bearer <API_SECRET_TOKEN>
    Body JSON:
      {
        "text": "I feel anxious and overwhelmed",
        "user_id": "optional_external_user_id"
      }
    Response:
      {
        "mood": "anxious",
        "intensity": "high",
        "sentiment": "negative",
        "emoji": "😰",
        "response": "AI comfort response...",
        "activities": ["...", "..."],
        "polarity": -0.45
      }

    Usage from another project (Python):
      import requests
      r = requests.post(
          'https://yourapp.com/api/analyze/',
          headers={'Authorization': 'Bearer your_token'},
          json={'text': 'I feel stressed today'}
      )
      data = r.json()
      print(data['mood'])       # 'anxious'
      print(data['response'])   # AI comfort message
    """
    if not _verify_token(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        body      = json.loads(request.body)
        user_text = body.get('text', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if not user_text:
        return JsonResponse({'error': 'text field is required'}, status=400)

    if len(user_text) > 2000:
        return JsonResponse({'error': 'text too long (max 2000 chars)'}, status=400)

    mood_data   = _analyzer.analyze(user_text)
    ai_response = _llm.get_response(user_text, mood_data)

    return JsonResponse({
        'mood':       mood_data['primary_mood'],
        'intensity':  mood_data['intensity'],
        'sentiment':  mood_data['sentiment'],
        'emoji':      mood_data['emoji'],
        'polarity':   mood_data['polarity'],
        'vader':      mood_data['vader_compound'],
        'response':   ai_response,
        'activities': mood_data['activities'],
    })


@require_GET
def health_check(request):
    """GET /api/health/ — check if the service is running"""
    return JsonResponse({
        'status':    'healthy',
        'llm':       _llm.backend,
        'groq_configured': bool(_llm.groq_key),
    })


@csrf_exempt
def history_api(request):
    """GET /api/history/?user_id=123 — fetch session history"""
    if not _verify_token(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    return JsonResponse({'message': 'History endpoint ready'})
