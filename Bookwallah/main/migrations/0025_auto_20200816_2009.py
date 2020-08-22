# Generated by Django 3.0.6 on 2020-08-16 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20200816_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='secret_file',
            field=models.FileField(blank=True, null=True, upload_to='documents'),
        ),
        migrations.AlterField(
            model_name='npsscore',
            name='chapter',
            field=models.CharField(blank=True, choices=[('West Bengal', 'West Bengal'), ('East', 'East'), ('Karnataka', 'Karnataka')], max_length=30, null=True, verbose_name='Chapter'),
        ),
    ]