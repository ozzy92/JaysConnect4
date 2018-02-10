

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Game


# Create your views here.
def login(request):
    """
    Write your login view here
    :param request:
    :return:
    """
    return HttpResponse('Login Here!')

def logout(request):
    """
    write your logout view here
    :param request:
    :return:
    """
    return HttpResponse('Logout Here!')

def signup(request):
    """
    write your user sign up view here
    :param request:
    :return:
    """
    return HttpResponse('Signup Here!')

def games(request):
    """
    Write your view which controls the game set up and selection screen here
    :param request:
    :return:
    """
    return render(request, 'connect4/games.html')

def play(request, pk):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :return:
    """
    return render(request, 'connect4/play.html', { 'game_pk' : pk} )
