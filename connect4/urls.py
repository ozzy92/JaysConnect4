from django.conf.urls import url
from django.urls import path
from django.http import HttpResponseRedirect
from . import views, rester, partial_views

urlpatterns = [    
    url(r'^$', lambda r: HttpResponseRedirect('games')),    # redirect root to games
    path('games/', views.games),
    path('play/<int:pk>/', views.play),
    path('rester/create_game/', rester.create_game),

    # view snippets used by ajax
    path('available_games/', partial_views.AvailableGames.as_view()),
    path('running_games/', partial_views.RunningGames.as_view()),
    path('user_games/', partial_views.UserGames.as_view()),
]

