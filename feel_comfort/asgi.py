import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feel_comfort.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chatbot.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chatbot.routing.websocket_urlpatterns)
    ),
})
