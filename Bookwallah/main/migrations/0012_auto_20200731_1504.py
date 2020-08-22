# Generated by Django 3.0.6 on 2020-07-31 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20200731_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChildPsychologyScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter', models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('East', 'East'), ('West Bengal', 'West Bengal')], max_length=30, null=True, verbose_name='Chapter (Child Psychology)')),
                ('month', models.CharField(blank=True, choices=[('JAN', 'JAN'), ('FEB', 'FEB'), ('MAR', 'MAR'), ('APR', 'APR'), ('MAY', 'MAY'), ('JUN', 'JUN'), ('JUL', 'JUL'), ('AUG', 'AUG'), ('SEP', 'SEP'), ('OCT', 'OCT'), ('NOV', 'NOV'), ('DEC', 'DEC')], max_length=10, null=True, verbose_name='Month (Child Psychology)')),
                ('year', models.CharField(blank=True, max_length=10, null=True, verbose_name='Year (Child Psychology)')),
                ('empathy', models.CharField(blank=True, max_length=10, null=True, verbose_name='Empathy Score (%) (Child Psychology)')),
                ('hope', models.CharField(blank=True, max_length=10, null=True, verbose_name='Hope Score (%) (Child Psychology)')),
                ('perseverance', models.CharField(blank=True, max_length=10, null=True, verbose_name='Perseverance Score (%) (Child Psychology)')),
                ('pro_social_conduct', models.CharField(blank=True, max_length=10, null=True, verbose_name='Pro Social Conduct Score (%) (Child Psychology)')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='child_survey_project_name', to='main.Project', verbose_name='Project (Child Psychology)')),
            ],
        ),
        migrations.CreateModel(
            name='NPSScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter', models.CharField(blank=True, choices=[('Karnataka', 'Karnataka'), ('East', 'East'), ('West Bengal', 'West Bengal')], max_length=30, null=True, verbose_name='Chapter (NPS Score)')),
                ('month', models.CharField(blank=True, choices=[('JAN', 'JAN'), ('FEB', 'FEB'), ('MAR', 'MAR'), ('APR', 'APR'), ('MAY', 'MAY'), ('JUN', 'JUN'), ('JUL', 'JUL'), ('AUG', 'AUG'), ('SEP', 'SEP'), ('OCT', 'OCT'), ('NOV', 'NOV'), ('DEC', 'DEC')], max_length=10, null=True, verbose_name='Month (NPS Score)')),
                ('year', models.CharField(blank=True, max_length=10, null=True, verbose_name='Year (NPS Score)')),
                ('score', models.CharField(blank=True, max_length=10, null=True, verbose_name='Score (%) (NPS Score)')),
            ],
        ),
        migrations.DeleteModel(
            name='NPS',
        ),
    ]
