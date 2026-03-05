"""
Chatbot Views — Feel Comfort
Handles: Text chat, Voice processing, History, Dashboard
"""

import json
import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count

from .models import MoodSession, UserMoodStats, DailyMoodLog
from .mood_analyzer import MoodAnalyzer
from .llm_handler import LLMHandler

# Singletons — initialized once when server starts
_analyzer = MoodAnalyzer()
_llm      = LLMHandler()


@login_required
def chat_view(request):
    """Main chat page"""
    recent = MoodSession.objects.filter(user=request.user).select_related('user')[:15]

    # Mood distribution for the mini chart
    stats = MoodSession.objects.filter(user=request.user).values(
        'detected_mood'
    ).annotate(count=Count('id')).order_by('-count')

    mood_chart = {s['detected_mood']: s['count'] for s in stats}

    try:
        user_stats = request.user.mood_stats
    except UserMoodStats.DoesNotExist:
        user_stats = None

    return render(request, 'chatbot/chat.html', {
        'recent_sessions': recent,
        'mood_chart':      json.dumps(mood_chart),
        'user_stats':      user_stats,
    })


@login_required
@require_POST
def process_text(request):
    """Process text message → mood analysis → LLM response"""
    try:
        data      = json.loads(request.body)
        user_text = data.get('message', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not user_text:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    if len(user_text) > 2000:
        return JsonResponse({'error': 'Message too long (max 2000 chars)'}, status=400)

    return _process_and_respond(request, user_text, 'text')


@login_required
@require_POST
def process_voice(request):
    """Process voice-to-text → mood analysis → LLM response"""
    try:
        data       = json.loads(request.body)
        voice_text = data.get('voice_text', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not voice_text:
        return JsonResponse({'error': 'No voice text received'}, status=400)

    return _process_and_respond(request, voice_text, 'voice')


def _process_and_respond(request, user_text: str, input_type: str):
    """Shared pipeline: NLP → LLM → Save to MySQL → Return JSON"""

    # 1. NLP mood analysis
    mood_data = _analyzer.analyze(user_text)

    # 2. LLM response (timed for monitoring)
    start = time.time()
    ai_response = _llm.get_response(user_text, mood_data)
    response_ms = int((time.time() - start) * 1000)

    # Determine which backend was actually used
    llm_used = 'fallback'
    if _llm.backend == 'groq' and _llm.groq_key:
        llm_used = 'groq'
    elif _llm.backend in ('ollama', 'groq'):
        llm_used = 'ollama'

    # 3. Save to MySQL
    session = MoodSession.objects.create(
        user            = request.user,
        user_input_text = user_text,
        detected_mood   = mood_data['primary_mood'],
        mood_intensity  = mood_data['intensity'],
        sentiment       = mood_data['sentiment'],
        polarity_score  = mood_data['polarity'],
        vader_compound  = mood_data['vader_compound'],
        ai_response     = ai_response,
        llm_used        = llm_used,
        input_type      = input_type,
        response_time_ms = response_ms,
    )

    # 4. Update aggregated stats
    stats, _ = UserMoodStats.objects.get_or_create(user=request.user)
    stats.update(mood_data['primary_mood'], mood_data['polarity'])

    # 5. Update user session counter
    request.user.total_sessions += 1
    request.user.save(update_fields=['total_sessions'])

    return JsonResponse({
        'success':    True,
        'session_id': session.id,
        'mood':       mood_data['primary_mood'],
        'intensity':  mood_data['intensity'],
        'sentiment':  mood_data['sentiment'],
        'emoji':      mood_data['emoji'],
        'activities': mood_data['activities'],
        'response':   ai_response,
        'llm_used':   llm_used,
        'response_ms': response_ms,
    })


@login_required
def mood_history(request):
    """Return user's full mood history as JSON (for AJAX/API)"""
    sessions = MoodSession.objects.filter(user=request.user).values(
        'id', 'detected_mood', 'mood_intensity', 'sentiment',
        'user_input_text', 'ai_response', 'input_type', 'created_at'
    )[:50]

    mood_counts = {}
    for s in sessions:
        m = s['detected_mood']
        mood_counts[m] = mood_counts.get(m, 0) + 1
        s['created_at'] = s['created_at'].strftime('%Y-%m-%d %H:%M')

    return JsonResponse({
        'sessions':   list(sessions),
        'mood_counts': mood_counts,
        'total':      len(sessions),
    })


@login_required
def dashboard_view(request):
    """Analytics dashboard — mood trends, charts"""
    sessions = MoodSession.objects.filter(user=request.user)
    total    = sessions.count()

    mood_dist = list(sessions.values('detected_mood').annotate(
        count=Count('id')
    ).order_by('-count'))

    daily_log = list(DailyMoodLog.objects.filter(
        user=request.user
    ).values('log_date', 'dominant_mood', 'session_count')[:30])

    try:
        stats = request.user.mood_stats
    except UserMoodStats.DoesNotExist:
        stats = None

    return render(request, 'chatbot/dashboard.html', {
        'total':      total,
        'mood_dist':  json.dumps(mood_dist, default=str),
        'daily_log':  json.dumps(daily_log, default=str),
        'stats':      stats,
    })
