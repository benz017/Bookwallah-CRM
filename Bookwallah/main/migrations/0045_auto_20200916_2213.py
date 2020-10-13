# Generated by Django 3.0.6 on 2020-09-16 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20200910_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='highlight',
            name='chapter',
            field=models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('West Bengal', 'West Bengal'), ('East', 'East')], max_length=30, null=True, unique=True, verbose_name='Chapter'),
        ),
        migrations.AlterField(
            model_name='issues',
            name='chapter',
            field=models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('West Bengal', 'West Bengal'), ('East', 'East')], max_length=30, null=True, unique=True, verbose_name='Chapter'),
        ),
        migrations.AlterField(
            model_name='npsscore',
            name='chapter',
            field=models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('West Bengal', 'West Bengal'), ('East', 'East')], max_length=30, null=True, verbose_name='Chapter'),
        ),
    ]
