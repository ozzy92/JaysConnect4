
from .models import Game
from django.views import generic

class GamesList(generic.ListView):
    template_name = 'connect4/game_list.html'
    context_object_name = 'games'

    def get_queryset(self):
        return Game.objects.filter(status = self.status.value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'list_name' : self.list_name,
            'list_id' : self.list_id,            
        })
        return context

class AvailableGames(GamesList):
    ''' generic list view for available games list '''
    list_name = 'Available Games'
    list_id = 'available_games'
    status = Game.Status.AVAILABLE

class RunningGames(GamesList):
    ''' generic list view for available games list '''
    list_name = 'Games in Progress'
    list_id = 'running_games'
    status = Game.Status.RUNNING

class UserGames(GamesList):
    ''' generic list view for available games list '''
    list_name = 'Your Previous Games'
    list_id = 'running_games'

    def get_queryset(self):
        # FIXME: implement!
        return []
