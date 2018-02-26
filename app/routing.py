
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.conf.urls import url
from django.urls import path, include
import connect4.routing
from connect4 import consumers

application = ProtocolTypeRouter({
    "websocket" : AuthMiddlewareStack(
        URLRouter([
            path('connect4ws/', include(connect4.routing)),
        ])
    ),
    "channel" : ChannelNameRouter(
        connect4.routing.channel_names
    ),
})
