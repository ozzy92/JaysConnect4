
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Game
from .consumers import GamesConsumer, PlayConsumer

# this file is for 'rester' models that return json results
# I could probably try the rester framework, but too many things to learn, and text/json is the same thing :)

@login_required
def create_game(request):
    ''' create a game, return game_id '''    
    new_game = Game(player1 = request.user.userplayer)
    new_game.save()
    id = new_game.pk
    response = json.dumps({ 'game_id' : id })
    GamesConsumer.send_available_update()
    return HttpResponse(response, content_type = 'text/json')

@login_required
def join_game(request, pk):
    ''' join a game, return true/false '''
    game = get_object_or_404(Game, pk = pk)
    response = game.join_up(request.user.userplayer)
    if response:
        GamesConsumer.send_available_update()
        GamesConsumer.send_running_update()
        PlayConsumer.send_play_update(game)
    response = json.dumps(response)
    return HttpResponse(response, content_type = 'text/json')

@login_required
def make_move(request, pk, column):
    ''' makes a move for the current player and updates the game '''
    game = get_object_or_404(Game, pk = pk)
    response = game.make_move(request.user.userplayer, column)
    if response:
        PlayConsumer.send_play_update(game)
        if game.status == Game.Status.FINISHED.value:
            GamesConsumer.send_running_update()
            GamesConsumer.send_user_update(game.player1)
            GamesConsumer.send_user_update(game.player2)
    response = json.dumps(response)
    return HttpResponse(response, content_type = 'text/json')
