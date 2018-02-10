
from django.urls import path
from . import consumers

urlpatterns = [    
    path('play/<int:pk>', consumers.PlayConsumer),
]
