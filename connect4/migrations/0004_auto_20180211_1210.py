# Generated by Django 2.0.2 on 2018-02-11 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connect4', '0003_auto_20180211_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.IntegerField(null=True),
        ),
    ]
