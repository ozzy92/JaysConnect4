

from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.views import generic
from .models import Game, Player, UserPlayer, ComputerPlayer
from .partial_views import BoardView


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
    ''' login a user using a form.  Docs say don't do this, but the LoginView looks complicated. '''
    error = None
    if request.method == 'POST':
        user = auth.authenticate(username = request.POST.get('username'), password = request.POST.get('password'))
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect('/connect4/')
            error = 'User is disabled. Contact adminstrator'
        else:
            error = 'Unknown user and password.  Try again'
    return render(request, 'connect4/login.html', context = { 'error' : error })
    

def logout(request):
    ''' logout a user, we don't care if it works, just redirect home '''
    auth.logout(request)
    return HttpResponseRedirect('/connect4/')


def signup(request):
    ''' registers a new user for the site '''
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            error = "Passwords don't match."
        elif len(password) < 6:
            error = "Password should be 6 or more characters."
        elif User.objects.filter(username = username):
            error = "Someone has used that username."
        else:
            try:
                user = User.objects.create_user(username, password = password, first_name = first_name)
                auth.login(request, user)                
            except Exception as e:
                error = e
            else:
                return HttpResponseRedirect('/connect4/')
    return render(request, 'connect4/signup.html', context = { 'error' : error })


def games(request):
    ''' games page '''
    Game.clean_abandoned()
    return render(request, 'connect4/games.html', header_context(request))


class PlayView(BoardView):
    model = Game
    template_name = 'connect4/play.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(header_context(self.request))
        return context
