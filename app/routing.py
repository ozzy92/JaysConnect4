
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.urls import path, include
import connect4.routing
from connect4 import consumers

application = ProtocolTypeRouter({
    "websocket" : AuthMiddlewareStack(
        URLRouter([
            path('connect4/', include(connect4.routing)),
        ])
    ),
})