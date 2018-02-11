from enum import Enum
import logging
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models


class Game(models.Model):
    class Status(Enum):
        AVAILABLE = 0
        RUNNING = 1
        FINISHED = 2
        ABANDONED = 3

    # board size
    ROWS = 6
    COLS = 7

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player1color = models.IntegerField(default = 0x000000) # black
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2', blank=True, null=True)
    player2color = models.IntegerField(default = 0xFF0000) # red
    status = models.IntegerField(default = Status.AVAILABLE.value)
    winner = models.IntegerField(default = None, blank = True, null = True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.winner:
            return '%s wins vs %s' % (self.winner_name, self.player1_name if self.winner == 2 else self.player2_name)
        else:
            return '%s vs %s%s' % (
                self.player1_name, self.player2_name or '(Click to Join)',
                ' (Abandoned)' if self.status == self.Status.ABANDONED.value else ''
            )

    @property
    def player1_name(self):
        return self.player1.get_short_name()

    @property
    def player1_color_web(self):
        return '#{0:06X}'.format(self.player1color)

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
    def start_date(self):
        coins = self.coin_set.order_by('created_date')
        if coins:
            return coins[0].created_date

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
    def last_action_date(self):
        return self.last_move.created_date

    @property
    def _build_board(self):
        ''' returns a tuple (board, col_full)
            board is a list of lists, rows of columns
                each cell is a list [player, color]; player is (1 or 2) or None (empty)
            col_full is a list of bools to specific if the column is full
        '''
        # FIXME: this does no validation, it assumes all the moves and players are valid
        board = [[(None, None) for col in range(self.COLS)] for row in range(self.ROWS)]
        for coin in self.coin_set.all():
            player = 1 if coin.player == self.player1 else 2 if coin.player == self.player2 else None
            color = self.player1color if player == 1 else self.player2color if player == 2 else None
            # color converted to web hex for the template
            board[coin.row][coin.column] = [player, '#{0:06X}'.format(color)]
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

    def join_up(self, player2):
        ''' join the game '''
        # FIXME: race condition not handled
        if self.player1 != player2:
            self.player2 = player2
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
                        # valid move, check if they won!  Add their coin to the board, so we don't need to reload
                        # FIXME: this is a race condition, I need to figure out how to do transactions
                        # if the user is really fast, they could try and place another coin                        
                        board[row_index][column] = (player_num, None)  # is_winner doesn't check color
                        if self._is_winner(board, row_index, column):
                            self.status = self.Status.FINISHED.value
                            self.winner = player_num
                            self.save()
                        # create the move
                        coin = self.coin_set.create(game=self, player=player, row=row_index, column=column)
                        coin.save()
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
            for (r, c) in cells:
                if board[r][c][0] == player:
                    sequential += 1
                    if sequential == 4:
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


class Coin(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    column = models.IntegerField()
    row = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s placed in column %d to drop in row %d' % (
            self.player.get_short_name(), self.column + 1, (Game.ROWS - self.row)
        )
