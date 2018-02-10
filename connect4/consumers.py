
from channels.generic.websocket import JsonWebsocketConsumer
import json

class PlayConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.accept()

    def receive_json(self, content):
        response = "You entered column %s" % content['play']
        self.send_json(response)

    def disconnect(self, close_code):
        pass
