from django.contrib import admin
from .models import Game

class GameAdmin(admin.ModelAdmin):
    ''' Helper for cleaning up the db, not really supposed to edit games '''

admin.site.register(Game, GameAdmin)


