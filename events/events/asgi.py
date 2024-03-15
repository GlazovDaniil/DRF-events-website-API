"""
ASGI config for events project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.sessions import CookieMiddleware, SessionMiddleware
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import urls

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'events.settings')

asgi = get_asgi_application()

application = ProtocolTypeRouter({
    "http": asgi,
    "websocket": CookieMiddleware(SessionMiddleware(URLRouter(urls.websocket_urlpatterns))),
})
