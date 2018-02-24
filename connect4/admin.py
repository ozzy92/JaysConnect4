from django.contrib import admin
from .models import Game, UserPlayer, ComputerPlayer

class GameAdmin(admin.ModelAdmin):
    ''' Helper for cleaning up the db, not really supposed to edit games '''

admin.site.register(Game, GameAdmin)

class UserPlayerAdmin(admin.ModelAdmin):
    ''' Helper for setting up user players manually '''

admin.site.register(UserPlayer, UserPlayerAdmin)

class ComputerPlayerAdmin(admin.ModelAdmin):
    ''' Helper for setting up computer players manually '''

admin.site.register(ComputerPlayer, ComputerPlayerAdmin)
