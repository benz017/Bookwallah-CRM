# Generated by Django 3.0.6 on 2020-10-10 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0060_auto_20201005_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='social_media',
            new_name='facebook',
        ),
        migrations.AddField(
            model_name='profile',
            name='instagram',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='linkedin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='skype',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='zoom',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
