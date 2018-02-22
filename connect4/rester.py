
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Game
from .consumers import GamesConsumer, PlayConsumer, CHANNEL_AVAILABLE, CHANNEL_RUNNING, CHANNEL_USER, CHANNEL_PLAY

# this file is for 'rester' models that return json results
# I could probably try the rester framework, but too many things to learn, and text/json is the same thing :)

@login_required
def create_game(request):
    ''' create a game, return game_id '''    
    new_game = Game(player1 = request.user)
    new_game.save()
    id = new_game.pk
    response = json.dumps({ 'game_id' : id })
    GamesConsumer.send_update(CHANNEL_AVAILABLE)
    return HttpResponse(response, content_type = 'text/json')

@login_required
def join_game(request, pk):
    ''' join a game, return true/false '''
    game = get_object_or_404(Game, pk = pk)
    response = game.join_up(request.user)
    if response:
        GamesConsumer.send_update(CHANNEL_AVAILABLE)
        GamesConsumer.send_update(CHANNEL_RUNNING)
        PlayConsumer.send_update(CHANNEL_PLAY % pk)
    response = json.dumps(response)
    return HttpResponse(response, content_type = 'text/json')

@login_required
def make_move(request, pk, column):
    ''' makes a move for the current player and updates the game '''
    game = get_object_or_404(Game, pk = pk)
    response = game.make_move(request.user, column)
    if response:
        PlayConsumer.send_update(CHANNEL_PLAY % pk)
        if game.status == Game.Status.FINISHED.value:
            GamesConsumer.send_update(CHANNEL_RUNNING)
            GamesConsumer.send_update(CHANNEL_USER % game.player1.get_short_name())
            GamesConsumer.send_update(CHANNEL_USER % game.player2.get_short_name())
    response = json.dumps(response)
    return HttpResponse(response, content_type = 'text/json')
