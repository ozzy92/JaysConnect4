from django.conf.urls import url
from django.urls import path
from django.http import HttpResponseRedirect
from . import views, rester, partial_views

urlpatterns = [    
    url(r'^$', lambda r: HttpResponseRedirect('games')),    # redirect root to games
    path('games/', views.games),
    path('play/<int:pk>/', views.PlayView.as_view()),

    # 'rester' views, just json gets
    path('rester/create_game/', rester.create_game),
    path('rester/join_game/<int:pk>/', rester.join_game),
    path('rester/game_board/<int:pk>/', partial_views.BoardView.as_view()),

    # view snippets used by ajax
    path('available_games/', partial_views.AvailableGames.as_view()),
    path('running_games/', partial_views.RunningGames.as_view()),
    path('user_games/', partial_views.UserGames.as_view()),
]

