# Generated by Django 3.1.2 on 2020-10-07 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music_metadata', '0002_auto_20201003_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='iswc',
            field=models.CharField(blank=True, max_length=13, null=True, unique=True),
        ),
    ]