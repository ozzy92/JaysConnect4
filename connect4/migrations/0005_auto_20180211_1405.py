# Generated by Django 2.0.2 on 2018-02-11 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connect4', '0004_auto_20180211_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
