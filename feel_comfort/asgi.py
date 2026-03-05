"""
ASGI config — enables real-time WebSocket connections with Daphne
"""
import os

# ⚠️ MUST be set before ANY Django or app imports so settings are configured first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feel_comfort.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chatbot.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(chatbot.routing.websocket_urlpatterns)
    ),
})
