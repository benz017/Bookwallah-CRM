# Generated by Django 3.0.6 on 2020-07-31 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20200731_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='npsscore',
            name='month',
        ),
        migrations.AddField(
            model_name='npsscore',
            name='quarter',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')], max_length=10, null=True, verbose_name='Quarter (NPS Score)'),
        ),
        migrations.AlterField(
            model_name='childpsychologyscore',
            name='chapter',
            field=models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('West Bengal', 'West Bengal'), ('East', 'East')], max_length=30, null=True, verbose_name='Chapter (Child Psychology)'),
        ),
        migrations.AlterField(
            model_name='npsscore',
            name='chapter',
            field=models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('West Bengal', 'West Bengal'), ('East', 'East')], max_length=30, null=True, verbose_name='Chapter (NPS Score)'),
        ),
    ]
