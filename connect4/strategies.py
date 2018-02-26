
import random

class StrategyBase():
    ''' base class for game player strategies '''

    def __init__(self, game, player):
        ''' initializes the strategy with the game, and the player the strategy is playing '''
        self.game = game
        self.player = player

    def start(self):
        ''' allows the strategy to start a work thread if needed '''
        pass

    def stop(self):
        ''' tells the strategy to clean up '''
        pass

    def reload_game(self):
        ''' updates the game object from the database.  Necessary when playing a human, and game is updated in rester '''
        self.game.refresh_from_db()

    def make_move(self):
        ''' tells the strategy to make it's next move, should call Game.make_move and return result '''
        pass


class RandomStrategy(StrategyBase):
    ''' Implements a random strategy that just moves randomly '''

    def make_move(self):
        available_columns = [i for (i, col) in enumerate(self.game.col_full)]
        column = random.choice(available_columns)
        return self.game.make_move(self.player, column)

class DumbStrategy(RandomStrategy):
    ''' Dumb strategy only looks to current move to win or prevent win, or make an adjacent move '''

class SmartStrategy(RandomStrategy):
    ''' Smart strategy build a scored depth search of possible moves then chooses the best it has so far '''

class LearningStrategy(SmartStrategy):
    ''' Learning strategy expands on smart strategy to adjust scoring based on previous history '''
