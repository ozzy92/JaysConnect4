
import asyncio
import datetime
import json
import logging
import random
import sys
import time
import threading
from asgiref.sync import async_to_sync, sync_to_async
from django.utils import timezone
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from .models import Game, ComputerPlayer, STRATEGIES
from . import strategies

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class GamesConsumer(AsyncJsonWebsocketConsumer):
    ''' Websocket from clients for games lists updates '''

    _CHANNEL_AVAILABLE = 'connect4.availablegames'
    _CHANNEL_RUNNING = 'connect4.runninggames'
    _CHANNEL_USER = 'connect4.usergames.%s'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_channel = None

    async def connect(self):
        ''' Add consumer to group channels '''
        await super().connect()
        self.user = self.scope['user']
        logger.info('Games connection; %s; user %s' % (self.channel_name, self.user))
        await self.channel_layer.group_add(self._CHANNEL_AVAILABLE, self.channel_name)
        await self.channel_layer.group_add(self._CHANNEL_RUNNING, self.channel_name)
        if self.user.is_authenticated:
            self.user_channel = self._CHANNEL_USER % self.user.get_short_name()
            await self.channel_layer.group_add(self.user_channel, self.channel_name)

    @classmethod
    def send_available_update(cls):
        cls._send_update(cls._CHANNEL_AVAILABLE)

    @classmethod
    def send_running_update(cls):
        cls._send_update(cls._CHANNEL_RUNNING)

    @classmethod
    def send_user_update(cls, player):
        cls._send_update(cls._CHANNEL_USER % player.get_short_name())

    @classmethod
    async def send_available_update_async(cls):
        await cls._send_update_async(cls._CHANNEL_AVAILABLE)

    @classmethod
    async def send_running_update_async(cls):
        await cls._send_update_async(cls._CHANNEL_RUNNING)

    @classmethod
    async def send_user_update_async(cls, player):
        await cls._send_update_async(cls._CHANNEL_USER % player.get_short_name())
    
    @classmethod
    def _send_update(cls, channel):
        ''' sends a games list update to all clients '''
        async_to_sync(cls._send_update_async)(channel)

    @classmethod
    async def _send_update_async(cls, channel):
        ''' sends a games list update to all clients '''
        logger.info('Sending games update to channel %s' % channel)
        if channel == cls._CHANNEL_AVAILABLE:
            list = 'available_games'
        elif channel == cls._CHANNEL_RUNNING:
            list = 'running_games'
        else:
            list = 'user_games'
        channel_layer = get_channel_layer()
        await channel_layer.group_send(channel, {'type' : 'games.update', 'list' : list })

    async def games_update(self, data):
        logger.info('Games update recieved, sending: %s; %s' % (self.channel_name, data))
        await self.send_json(data)

    async def disconnect(self, close_code):
        ''' Remove consumer from group channels '''
        logger.info('Games disconnect; %s' % self.channel_name)
        await self.channel_layer.group_discard(self._CHANNEL_AVAILABLE, self.channel_name)
        await self.channel_layer.group_discard(self._CHANNEL_RUNNING, self.channel_name)
        if self.user_channel:
            await self.channel_layer.group_discard(self.user_channel, self.channel_name)
        await super().disconnect(close_code)


class PlayConsumer(AsyncJsonWebsocketConsumer):
    ''' websockets from client for playing a game and getting game moves '''

    _CHANNEL_PLAY = 'connect4.play.%d'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.play_channel = None

    async def connect(self):
        ''' Add consumer to group channels '''
        await super().connect()
        logger.info('Play connection; %s' % self.channel_name)
        try:
            game = int(self.scope['url_route']['kwargs']['pk'])
        except:
            logger.exception('Invalid play connection received %s' % self.channel_name)
        else:
            self.play_channel = self._CHANNEL_PLAY % game
            logger.info('Play connection for channel %s for %s' % (self.play_channel, self.channel_name))
            await self.channel_layer.group_add(self.play_channel, self.channel_name)

    @classmethod
    def send_play_update(cls, game):
        ''' sends a game play update to clients '''
        async_to_sync(cls.send_play_update_async)(game)

    @classmethod
    async def send_play_update_async(cls, game):
        ''' sends a game play update to clients '''
        channel_layer = get_channel_layer()
        channel = cls._CHANNEL_PLAY % game.id
        logger.info('Sending async player update to channel %s' % channel)
        await channel_layer.group_send(channel, { 'type' : 'play.update', 'game' : game.id })

    async def play_update(self, data):
        ''' play update recieved, relay to clients '''
        logger.info('Games update received, sending: %s; %s' % (self.channel_name, data))
        await self.send_json(data)

    async def disconnect(self, close_code):        
        if self.play_channel:
            logger.info('Play Command disconnecting from channel %s for %s' % (self.play_channel, self.channel_name))
            await self.channel_layer.group_discard(self.play_channel, self.channel_name)
        await super().disconnect(close_code)


class GameSeedConsumer(AsyncConsumer):
    ''' This worker consumer creates games with computer players, and joins unstarted games '''
    
    SEEDED_GAMES = 5
    SEED_WAIT_MIN = 10
    SEED_WAIT_MAX = SEED_WAIT_MIN * 5
    JOIN_WAIT_MIN = 60
    JOIN_WAIT_MAX = JOIN_WAIT_MIN * 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._added = False
        self._join_games_schedule = set()

    @classmethod
    def register(cls):
        ''' tells seed consumer to start running '''
        logger.info('Seed sending register')
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            "game-seed",
            {
                "type" : "register.games"
            }
        )

    async def register_games(self, data):
        ''' setup to receive games updates '''
        logger.info('Seed register games received')
        if not self._added:
            self._added = True
            logger.info('Registering for group; %s' % self.channel_name)
            await self.channel_layer.group_add(GamesConsumer._CHANNEL_AVAILABLE, self.channel_name)
            await self._check_for_updates()

    async def games_update(self, data):
        ''' get a games update '''
        logger.info('Seed Games update; %s' % (self.channel_name))
        await self._check_for_updates()

    async def _check_for_updates(self):
        ''' schedules checks for new data '''
        self._seed_games_delayed()
        self._join_games_delayed()

    def _seed_games_delayed(self):
        ''' helper to schedule delayed seeding '''
        loop = asyncio.get_event_loop()
        wait = random.randint(self.SEED_WAIT_MIN, self.SEED_WAIT_MAX)
        logger.info('Sleeping %d to seed games' % wait)
        loop.call_later(wait, lambda : asyncio.ensure_future(self._seed_games()))

    async def _seed_games(self):
        ''' adds games with computer players '''
        logger.info('Seeding games')
        num_games = Game.objects.filter(status = Game.Status.AVAILABLE.value).count()
        if num_games < self.SEEDED_GAMES:
            logger.info('Adding new seeded game')
            player = random.choice(ComputerPlayer.objects.all())
            game = Game(player1 = player)
            game.save()
            await GamePlayerConsumer.send_play_game_async(game)
            await GamesConsumer.send_available_update_async()
            if num_games + 1 < self.SEEDED_GAMES:
                self._seed_games_delayed()

    def _join_games_delayed(self):
        ''' Schedule joining delay for waiting games '''
        logger.info('Checking for games to join')
        games = Game.objects.filter(status = Game.Status.AVAILABLE.value)
        loop = asyncio.get_event_loop()
        for game in games:
            if game.id not in self._join_games_schedule:
                wait = random.randint(self.JOIN_WAIT_MIN, self.JOIN_WAIT_MAX)
                logger.info('Waiting %d to join game %s' % (wait, game.id))
                loop.call_later(wait, lambda : asyncio.ensure_future(self._join_game(game.id)))
                self._join_games_schedule.add(game.id)
        
    async def _join_game(self, game_id):
        ''' Get any available games '''
        logger.info('Checking to join game %s' % game_id)
        game = Game.objects.get(pk = game_id)
        if game.status == Game.Status.AVAILABLE.value:
            logger.info('Joining game %s' % game)
            player = game.player1
            while player == game.player1:            
                player = random.choice(ComputerPlayer.objects.all())
            logger.info('Joining game %s; chose player %s' % (game, player))
            if game.join_up(player):
                logger.info('Joined game %s; player %s' % (game, player))
                await GamePlayerConsumer.send_play_game_async(game)
                await GamesConsumer.send_available_update_async()
                await GamesConsumer.send_running_update_async()
                await PlayConsumer.send_play_update_async(game)


class GamePlayerConsumer(AsyncConsumer):
    ''' This consumer plays a game as a computer player '''

    MOVE_DELAY = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # game players is a dictionary of (game, player) = strategy
        self._game_players = {}

    @classmethod
    async def send_play_game_async(cls, game):
        ''' tells consumer to start running '''
        logger.info('Game player sending playing to register computer player')
        channel_layer = get_channel_layer()
        await channel_layer.send(
            "game-player",
            {
                "type" : "play.game",
                "game" : game.id,                
            }
        )

    async def play_game(self, data):
        ''' Handles a new game to play, registers AI players to play the game '''
        logger.info('Game player got message to play game %s' % data)
        game_id = data['game']
        game = Game.objects.get(pk = game_id)
        for player in (game.player1, game.player2):
            if isinstance(player, ComputerPlayer):
                strategy_class = '%sStrategy' % STRATEGIES[player.strategy]
                strategy_class = getattr(strategies, strategy_class)
                strategy = strategy_class(game, player)
                strategy.start()
                self._game_players[game.id, player.id] = strategy
        play_channel = PlayConsumer._CHANNEL_PLAY % game.id
        await self.channel_layer.group_add(play_channel, self.channel_name)

    async def play_update(self, data):
        ''' play update recieved, relay to clients '''
        logger.info('Game player play update received, playing strategies: %s' % (data))
        game_id = data['game']
        game = Game.objects.get(pk = game_id)
        if game.status == Game.Status.RUNNING.value:
            player = game.next_move
            strategy = self._game_players.get((game_id, player.id))
            if strategy:
                async def move_delayed():
                    logger.info('Making move for %s in game %s; %s' % (player, game_id, game))
                    strategy.reload_game()
                    strategy.make_move()
                    await PlayConsumer.send_play_update_async(game)

                logger.info('Queuing move for %s in game %s; %s' % (player, game_id, game))
                loop = asyncio.get_event_loop()
                loop.call_later(self.MOVE_DELAY, lambda : asyncio.ensure_future(move_delayed()))
        elif game.status in (Game.Status.FINISHED.value, Game.Status.ABANDONED.value):
            for player in (game.player1, game.player2):
                if player:
                    strategy = self._game_players.get((game_id, player.id))
                    if strategy:
                        strategy.stop()
                        logger.info('Game over, removing %s from game %s; %s' % (player, game_id, game))
                        del self._game_players[(game_id, player.id)]
