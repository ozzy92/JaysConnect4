# Generated by Django 2.0.2 on 2018-02-23 22:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('connect4', '0006_coin_winner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wins', models.IntegerField(default=0, editable=False)),
                ('loses', models.IntegerField(default=0, editable=False)),
                ('abandoned', models.IntegerField(default=0, editable=False)),
            ],
        ),
        migrations.AlterField(
            model_name='game',
            name='player1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_1', to='connect4.Player'),
        ),
        migrations.AlterField(
            model_name='game',
            name='player2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_2', to='connect4.Player'),
        ),
        migrations.CreateModel(
            name='ComputerPlayer',
            fields=[
                ('player_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='connect4.Player')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('strategy', models.IntegerField(choices=[(1, 'Random - plays completely randomly'), (2, 'Dumb - only looks at current move, but not ahead'), (3, 'Smart - brute force depth search scoring strategy'), (4, 'Learning - learning model that adjusts strategy with history and pattern matching')], default=1)),
            ],
            bases=('connect4.player',),
        ),
        migrations.CreateModel(
            name='UserPlayer',
            fields=[
                ('player_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='connect4.Player')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('connect4.player',),
        ),
    ]