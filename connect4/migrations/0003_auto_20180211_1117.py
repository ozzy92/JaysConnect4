# Generated by Django 2.0.2 on 2018-02-11 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connect4', '0002_auto_20180210_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='player1color',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='player2color',
            field=models.IntegerField(default=16711680),
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
