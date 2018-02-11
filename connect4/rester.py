
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Game

# this file is for 'rester' models that return json results
# I could probably try the rester framework, but too many things to learn, and text/json is the same thing :)

@login_required
def create_game(request):
    ''' create a game, return game_id '''    
    new_game = Game(player1 = request.user)
    new_game.save()
    id = new_game.pk
    response = json.dumps({ 'game_id' : id })
    return HttpResponse(response, content_type = 'text/json')

@login_required
def join_game(request, pk):
    ''' join a game, return true/false '''
    game = get_object_or_404(Game, pk = pk)
    response = game.join_up(request.user)
    response = json.dumps(response)
    return HttpResponse(response, content_type = 'text/json')

@login_required
def make_move(request, pk, column):
    ''' makes a move for the current player and updates the game '''
    game = get_object_or_404(Game, pk = pk)
    response = game.make_move(request.user, column)
    response = json.dumps(response)
    return HttpResponse(response, content_type = 'text/json')
