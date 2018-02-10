
import json
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Game

# this file is for 'rester' models that return json results
# I could probably try the rester framework, but too many things to learn, and text/json is the same thing :)

def create_game(request):
    ''' create a game, return game_id '''
    # FIXME: enable authentication
    # FIXME: don't let players create more than one game
    jay = User.objects.filter(username = 'jay')[0]
    new_game = Game(player1 = jay)
    new_game.save()
    id = new_game.pk
    response = json.dumps({ 'game_id' : id })
    return HttpResponse(response, content_type = 'text/json')

def available_games(request):
    ''' return a list of games since the last request '''
    available_games = [game.id for game in Game.objects.filter(player2 = None)]
    response = json.dumps(available_games)
    return HttpResponse(response, content_type = 'text/json')

