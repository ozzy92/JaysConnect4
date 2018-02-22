
from django.urls import path
from . import consumers

urlpatterns = [    
    path('games/', consumers.GamesConsumer),
    path('play/<int:pk>/', consumers.PlayConsumer),
]
