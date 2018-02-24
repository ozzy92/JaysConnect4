from enum import Enum
import logging
import threading
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from polymorphic.models import PolymorphicModel


class Player(PolymorphicModel):
    ''' base model for players with stats '''
    wins = models.IntegerField(null = False, default = 0, editable = False)
    losses = models.IntegerField(null = False, default = 0, editable = False)
    draws = models.IntegerField(null = False, default = 0, editable = False)
    abandoned = models.IntegerField(null = False, default = 0, editable = False)

    def __str__(self):
        return '%d wins; %d losses; %d draws; %d abandoned' % (self.wins, self.losses, self.draws, self.abandoned)


class UserPlayer(Player):
    ''' User player, uses Django users for login '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def get_short_name(self):
        return self.user.get_short_name()

    def __str__(self):        
        return '%s - %s' % (self.get_short_name(), super().__str__())


# magic from here: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
# creates UserPlayer for each user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserPlayer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userplayer.save()


STRATEGIES = {
    1 : 'Random',
    2 : 'Dumb',
    3 : 'Smart',
    4 : 'Learning',
}
STRATEGY_DESCRIPTIONS = {
    1 : 'plays completely randomly',
    2 : 'only looks at current move, but not ahead',
    3 : 'brute force depth search scoring strategy',
    4 : 'learning model that adjusts strategy with history and pattern matching',
}

class ComputerPlayer(Player):
    ''' Computer player with strategy model '''
    STRATEGY_CHOICES = tuple(
        [
            (k, '%s - %s' % (STRATEGIES[k], STRATEGY_DESCRIPTIONS[k]))
            for k in sorted(STRATEGIES.keys())
        ]
    )

    name = models.CharField(max_length = 30, blank = False, null = False, unique = True)
    strategy = models.IntegerField(default = 1, blank = False, null = False, choices = STRATEGY_CHOICES)

    def get_short_name(self):
        return self.name

    def __str__(self):
        return '%s - %s - %s' % (self.get_short_name(), STRATEGIES[self.strategy], super().__str__())


class Game(models.Model):
    class Status(Enum):
        AVAILABLE = 0
        RUNNING = 1
        FINISHED = 2
        ABANDONED = 3

    # board size
    ROWS = 6
    COLS = 7

    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_1')
    player1color = models.IntegerField(default = 0x000000) # black
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_2', blank=True, null=True)
    player2color = models.IntegerField(default = 0xFF0000) # red
    status = models.IntegerField(default = Status.AVAILABLE.value)
    winner = models.IntegerField(default = None, blank = True, null = True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):        
        player1 = self.winner_name if self.winner else self.player1_name
        player2 = ((self.player1_name if self.winner == 2 else self.player2_name)
                   if self.winner_name else self.player2_name)
        return '%s %s %s%s%s' % (
            self.player1_name, 
            'wins vs' if self.winner_name else 'draws' if self.is_draw else 'vs',
            self.player2_name or '(Click to Join)',
            ' (%s)' % self.last_action_date.strftime('%b %d %y')
             if self.status in (self.Status.FINISHED.value, self.Status.ABANDONED.value) else '',
            ' (Abandoned)' if self.status == self.Status.ABANDONED.value else ''
        )

    @property
    def player1_user(self):
        return self.player1.user if isinstance(self.player1, UserPlayer) else None

    @property
    def player1_name(self):
        return self.player1.get_short_name()

    @property
    def player1_color_web(self):
        return '#{0:06X}'.format(self.player1color)

    @property
    def player2_user(self):
        return self.player2.user if isinstance(self.player2, UserPlayer) else None

    @property
    def player2_name(self):        
        return self.player2.get_short_name() if self.player2 else ''

    @property
    def player2_color_web(self):
        return '#{0:06X}'.format(self.player2color)

    @property
    def winner_name(self):
        return self.player1_name if self.winner == 1 else self.player2_name if self.winner == 2 else None

    @property
    def is_draw(self):
        # game is a draw if board fills up!
        # FIXME: no validation... 
        return self.status == self.Status.FINISHED.value and not self.winner

    @property
    def start_time(self):
        ''' this returns either the first move, or ceated time if no moves '''
        coins = self.coin_set.order_by('created_date')
        return coins[0].created_date if coins else self.created_date

    @property
    def last_move(self):        
        last_move = self.coin_set.order_by('-created_date')
        if last_move:
            return last_move[0]
    
    @property
    def next_move(self):
        ''' Retuns the user with the next move, if there are 2 players, and the game isn't over '''
        last_move = self.last_move
        if self.player1 and self.player2 and self.status == self.Status.RUNNING.value:
            if last_move:
                return self.player1 if last_move.player == self.player2 else self.player2
            else:
                # FIXME: make more fair with random starter
                return self.player1

    @property
    def next_move_user(self):
        return self.next_move.user if isinstance(self.next_move, UserPlayer) else None

    @property
    def last_action_date(self):
        return self.last_move.created_date if self.last_move else self.start_time

    @property
    def _build_board(self):
        ''' returns a tuple (board, col_full)
            board is a list of lists, rows of columns
                each cell is a list [player, color, win];
                    player is (1 or 2) or None (empty), win is True if winning move
            col_full is a list of bools to specific if the column is full
        '''
        # FIXME: this does no validation, it assumes all the moves and players are valid
        board = [[(None, None) for col in range(self.COLS)] for row in range(self.ROWS)]
        for coin in self.coin_set.all():
            player = 1 if coin.player == self.player1 else 2 if coin.player == self.player2 else None
            color = self.player1color if player == 1 else self.player2color if player == 2 else None
            # color converted to web hex for the template
            board[coin.row][coin.column] = [player, '#{0:06X}'.format(color), coin.winner]
        col_full = [all(board[row][col][0] for row in range(self.ROWS)) for col in range(self.COLS)]
        return (board, col_full)

    @property
    def board(self):
        ''' returns the board from _build_board for the template to use '''
        return self._build_board[0]
        
    @property
    def col_full(self):
        ''' retuns col_full from _build_board for the template to use '''
        return self._build_board[1]

    def join_up(self, user):
        ''' join the game '''
        # FIXME: race condition not handled
        if self.player1_user != user and not self.player2:
            self.player2 = user.userplayer
            self.status = self.Status.RUNNING.value
            self.save()
            return True
        else:
            return False

    def make_move(self, player, column):
        ''' make a move for the given player and column '''
        # validate correct player, and column range
        if player == self.next_move and 0 <= column < self.COLS:
            player_num = 1 if self.player1 == player else 2
            (board, col_full) = self._build_board
            if not self.col_full[column]:
                # determine the row the coin falls to
                for (row_index, row) in enumerate(board):
                    if not row[column][0]:
                        # valid move, create the move
                        coin = self.coin_set.create(game=self, player=player, row=row_index, column=column)
                        coin.save()
                        # check if they won!  Add their coin to the board, so we don't need to reload
                        # FIXME: this is a race condition, I need to figure out how to do transactions
                        # if the user is really fast, they could try and place another coin                        
                        board[row_index][column] = (player_num, None, False)
                        if self._is_winner(board, row_index, column):
                            self.status = self.Status.FINISHED.value
                            self.winner = player_num
                            self.save()
                        # no winner, see if it's a draw
                        elif len(self.coin_set.all()) == self.ROWS * self.COLS:
                            self.status = self.Status.FINISHED.value
                            self.save()                            
                        return True
        logging.warning('Invalid move received %s, %s, %s' % (self.id, player.username, column))
        return False

    def _is_winner(self, board, row, column):
        ''' Helper to find if the last move is a winner, returns True if winning move
            Only checks the last move, which is player from row, column on the board
        '''
        player = board[row][column][0]
        def _four_in_a_row(cells):
            ''' helper to loop through cell sequence that is adjacent, list of tuple (row, col) '''
            sequential = 0
            for (i, (r, c)) in enumerate(cells):
                if board[r][c][0] == player:
                    sequential += 1
                    if sequential == 4:
                        # found a winner, mark the board
                        self._mark_winners(cells[i-3:i+1])
                        return True
                else:
                    sequential = 0
            return False
        # build lists of winning lists
        cells_lists = [
            # verticle
            [(r, column) for r in range(self.ROWS)],
            # horizontal
            [(row, c) for c in range(self.COLS)],
            # diagnally upper left to lower right (reverse y coordinate, not screen)
            [(row + offset, column + offset) for offset
                in range(- max(row, column), max(self.ROWS, self.COLS))
                if 0 <= row + offset < self.ROWS and 0 <= column + offset < self.COLS],
            # diagnally upper right to lower left (reverse y coordinate, not screen)
            [(row - offset, column + offset) for offset
                in range(- max(row, column), max(self.ROWS, self.COLS))
                if 0 <= row - offset < self.ROWS and 0 <= column + offset < self.COLS],
        ]
        is_winner = any(_four_in_a_row(cells) for cells in cells_lists)
        return is_winner

    def _mark_winners(self, cells):
        ''' marks winning coins '''
        for coin in self.coin_set.all():
            (r, c) = (coin.row, coin.column)
            if (r, c) in cells:
                coin.winner = True
                coin.save()

    @property
    def _is_abandoned(self):
        ''' deterimes if this game has been abandoned (with no moves after an hour) '''
        if self.status in (self.Status.AVAILABLE.value, self.Status.RUNNING.value):
            now = timezone.now()
            last_change = self.last_move.created_date if self.last_move else self.start_time
            delta = now - last_change
            return (delta.total_seconds() > 60 * 60)
        return False
        
    @classmethod
    def clean_abandoned(cls):
        ''' This method cleans up abandoned games in a new thread
            We are defining an abandoned game to be one with more than an hour with no move
        '''
        # this page kicks off an abandoned game thread... no idea if this is a good way!
        # https://stackoverflow.com/questions/21945052/simple-approach-to-launching-background-task-in-django
        def clean():
            for game in Game.objects.all():
                if game._is_abandoned:
                    game.status = Game.Status.ABANDONED.value
                    game.save()
        threading.Thread(target = clean, daemon = True).start()


class Coin(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    column = models.IntegerField()
    row = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)
    winner = models.BooleanField(default = False)

    def __str__(self):        
        last = self == self.game.last_move
        return '%s column %d, for row %d%s' % (
            self.player.get_short_name(), self.column + 1, (Game.ROWS - self.row),
            ', To Win!' if last and self.winner else ', To Draw!' if last and self.game.is_draw else ''
        )
