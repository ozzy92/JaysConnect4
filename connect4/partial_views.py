
from .models import Game
from django.views import generic
from django.db.models import Q

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
    list_id = 'user_games'

    def get_queryset(self):
        games = Game.objects.filter(Q(status = Game.Status.FINISHED.value) &
                                    (Q(player1 = self.request.user) | Q(player2 = self.request.user)))
        # limit to 50, in case someone really likes it
        games = games[:50]
        return games


class BoardView(generic.DetailView):
    ''' game board view '''
    model = Game
    template_name = 'connect4/board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.object
        context.update({
            'is_player1' : game.player1 == self.request.user,
            'is_player2' : game.player2 == self.request.user,
            'next_move' : game.next_move.get_short_name() if game.next_move else None,
            'is_user_move' : game.next_move == self.request.user,
        })
        return context
 