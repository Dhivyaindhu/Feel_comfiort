"""
WebSocket Consumer — Real-time streaming chat
Allows LLM response to stream word-by-word (like ChatGPT typing effect)
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import get_user
from asgiref.sync import sync_to_async
from .mood_analyzer import MoodAnalyzer
from .llm_handler import LLMHandler
from .models import MoodSession, UserMoodStats

_analyzer = MoodAnalyzer()
_llm      = LLMHandler()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time mood chat.
    Connect: ws://yoursite.com/ws/chat/
    """

    async def connect(self):
        # Use get_user() — properly async-safe way to access the user.
        # Accessing self.scope['user'] directly triggers a synchronous DB
        # lookup via SimpleLazyObject, causing SynchronousOnlyOperation.
        self.user = await get_user(self.scope)
        if self.user.is_anonymous:
            await self.close()
            return
        await self.accept()
        await self.send(text_data=json.dumps({
            'type':    'connected',
            'message': f'Connected! Hi {self.user.username} 💙',
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data       = json.loads(text_data)
            user_text  = data.get('message', '').strip()
            input_type = data.get('input_type', 'text')

            if not user_text:
                return

            # NLP — wrap with sync_to_async so blocking NLTK/TextBlob work
            # runs safely in a thread pool instead of blocking the event loop
            mood_data = await sync_to_async(_analyzer.analyze)(user_text)

            # Send mood immediately (before LLM responds)
            await self.send(text_data=json.dumps({
                'type':      'mood_detected',
                'mood':      mood_data['primary_mood'],
                'intensity': mood_data['intensity'],
                'emoji':     mood_data['emoji'],
                'sentiment': mood_data['sentiment'],
            }))

            # LLM response
            await self.send(text_data=json.dumps({
                'type': 'thinking',
                'message': '💭 ComfortBot is thinking...',
            }))

            # LLM makes blocking HTTP requests — run in thread via sync_to_async
            ai_response = await sync_to_async(_llm.get_response)(user_text, mood_data)

            # Save to DB — use database_sync_to_async for ORM operations
            session = await database_sync_to_async(self._save_session)(
                user_text, mood_data, ai_response, input_type
            )

            # Send full response
            await self.send(text_data=json.dumps({
                'type':       'response',
                'response':   ai_response,
                'activities': mood_data['activities'],
                'session_id': session.id,
            }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                'type':  'error',
                'message': f'Something went wrong: {str(e)}',
            }))

    def _save_session(self, user_text, mood_data, ai_response, input_type):
        # self.user is already resolved (set in connect), safe to use here
        session = MoodSession.objects.create(
            user            = self.user,
            user_input_text = user_text,
            detected_mood   = mood_data['primary_mood'],
            mood_intensity  = mood_data['intensity'],
            sentiment       = mood_data['sentiment'],
            polarity_score  = mood_data['polarity'],
            vader_compound  = mood_data['vader_compound'],
            ai_response     = ai_response,
            input_type      = input_type,
        )
        stats, _ = UserMoodStats.objects.get_or_create(user=self.user)
        stats.update(mood_data['primary_mood'], mood_data['polarity'])
        return session
