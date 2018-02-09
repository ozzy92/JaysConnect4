from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.db import models

# Create your models here.

@python_2_unicode_compatible
class Game(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2', blank=True, null=True)
    status = models.CharField(max_length=10)
    winner = models.CharField(max_length=10)
    created_date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        if self.player2:
            return ' vs '.join([self.player1.get_full_name(), self.player2.get_full_name()])

        else:
            return 'Join now to play %s'%self.player1.get_short_name()

    @property
    def start_date(self):
        return self.coin_set.order_by('created_date')[0].created_date

    @property
    def last_move(self):
        return self.coin_set.order_by('-created_date')[0]

    @property
    def last_action_date(self):
        return self.last_move.created_date

    def join_up(self, player_2):
        if self.player2 is None:
            self.player2 = player_2
            self.save()
            return True
        else:
            return False

    def make_move(self, player, row, column):
        try:
             self.coin_set.create(game=self, player=player, row=row, column=column)
        except:
             return False

        return True

@python_2_unicode_compatible
class Coin(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    column = models.IntegerField()
    row = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return ' '.join([
            self.player, 'to', self.row, self.column
        ])
