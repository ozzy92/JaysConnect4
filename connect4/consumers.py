
import asyncio
import json
import logging
import random
import sys
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from .models import Game, ComputerPlayer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

CHANNEL_AVAILABLE = 'connect4.availablegames'
CHANNEL_RUNNING = 'connect4.runninggames'
CHANNEL_USER = 'connect4.usergames.%s'

CHANNEL_PLAY = 'connect4.play.%d'


class GamesConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        ''' Add consumer to group channels '''
        await super().connect()
        self.user = self.scope['user']
        logger.info('Games connection; %s; user %s' % (self.channel_name, self.user))
        await self.channel_layer.group_add(CHANNEL_AVAILABLE, self.channel_name)
        await self.channel_layer.group_add(CHANNEL_RUNNING, self.channel_name)
        if self.user.is_authenticated:
            self.user_channel = CHANNEL_USER % self.user.get_short_name()
            await self.channel_layer.group_add(self.user_channel, self.channel_name)

    @classmethod
    def send_update(cls, channel):
        ''' sends a group channel broadcast to these consumers '''
        if channel == CHANNEL_AVAILABLE:
            list = 'available_games'
        elif channel == CHANNEL_RUNNING:
            list = 'running_games'
        else:
            list = 'user_games'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(channel, {'type' : 'games.update', 'list' : list })

    async def games_update(self, data):
        logger.info('Games update; %s; %s' % (self.channel_name, data))
        await self.send_json(data)

    async def disconnect(self, close_code):
        ''' Remove consumer from group channels '''
        logger.info('Games disconnect; %s' % self.channel_name)
        await self.channel_layer.group_discard(CHANNEL_AVAILABLE, self.channel_name)
        await self.channel_layer.group_discard(CHANNEL_RUNNING, self.channel_name)
        if hasattr(self, self.user_channel):
            await self.channel_layer.group_discard(self.user_channel, self.channel_name)
        await super().disconnect(close_code)


class PlayConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        ''' Add consumer to group channels '''
        await super().connect()
        logger.info('Play connection; %s' % self.channel_name)
        try:
            game = int(self.scope['url_route']['kwargs']['pk'])
        except:
            logger.exception('Invalid play connection received %s' % self.channel_name)
        else:
            self.play_channel = CHANNEL_PLAY % game
            logger.info('Play connection for channel %s for %s' % (self.play_channel, self.channel_name))
            await self.channel_layer.group_add(self.play_channel, self.channel_name)

    @classmethod
    def send_update(cls, channel):
        ''' sends a group channel broadcast to these consumers '''
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(channel, {'type' : 'play.update' })

    async def play_update(self, data):
        logger.info('Games update; %s; %s' % (self.channel_name, data))
        await self.send_json(data)

    async def disconnect(self, close_code):        
        if hasattr(self, 'play_channel'):
            logger.info('Play Command disconnecting from channel %s for %s' % (self.play_channel, self.channel_name))
            await self.channel_layer.group_discard(self.play_channel, self.channel_name)
        await super().disconnect(close_code)


class GameSeedConsumer(SyncConsumer):
    ''' This consumer creates games with computer players '''
    
    SEEDED_GAMES = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._added = False

    @classmethod
    def register(cls):
        ''' tells seed consumer to start running '''
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            "game-seed",
            {
                "type" : "register.games"
            }
        )

    def register_games(self, data):
        ''' setup to receive games updates '''
        logger.info('Seed register games')
        if not self._added:
            self._added = True
            logger.info('Registering for group; %s' % self.channel_name)
            async_to_sync(self.channel_layer.group_add)(CHANNEL_AVAILABLE, self.channel_name)
        self._seed_games()

    def games_update(self, data):
        ''' get a games update '''
        logger.info('Seed Games update; %s' % (self.channel_name))
        self._seed_games()
        self._join_games()

    def _seed_games(self):
        ''' adds games with computer players '''
        logger.info('Seeding games')
        num_games = Game.objects.filter(status = Game.Status.AVAILABLE.value).count()
        if num_games < self.SEEDED_GAMES:
            logger.info('Adding new seeded game')
            player = random.choice(ComputerPlayer.objects.all())
            Game(player1 = player).save()
            GamesConsumer.send_update(CHANNEL_AVAILABLE)

    def _join_games(self):
        ''' joins games after they are available for more than 60 seconds '''


class GamePlayerConsumer(SyncConsumer):
    ''' This consumer plays a game as a computer player '''

