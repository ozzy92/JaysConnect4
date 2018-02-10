

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Game

def header_context(request):
    ''' helper to get the header context '''
    authenticated = request.user.is_authenticated
    user = request.user.get_short_name() if authenticated else 'Anonymous'
    context = {
        'authenticated' : authenticated,
        'user' : user
    }
    return context

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
    ''' games page '''
    return render(request, 'connect4/games.html', header_context(request))

def play(request, pk):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :return:
    """
    return render(request, 'connect4/play.html', { 'game_pk' : pk} )
