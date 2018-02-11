

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.views import generic
from .models import Game
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


class PlayView(BoardView):
    model = Game
    template_name = 'connect4/play.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(header_context(self.request))
        return context
