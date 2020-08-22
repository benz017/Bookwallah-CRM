# Generated by Django 3.0.6 on 2020-08-21 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20200820_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='npsscore',
            name='chapter',
            field=models.CharField(blank=True, choices=[('West Bengal', 'West Bengal'), ('East', 'East'), ('Karnataka', 'Karnataka')], max_length=30, null=True, verbose_name='Chapter'),
        ),
        migrations.CreateModel(
            name='Pledge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pledge', models.CharField(blank=True, max_length=400, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('donor', models.ForeignKey(default=2, on_delete=django.db.models.deletion.DO_NOTHING, related_name='pledge_donor', to='main.Donor')),
            ],
        ),
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(blank=True, max_length=300, null=True)),
                ('value', models.CharField(blank=True, max_length=32, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('donor', models.ForeignKey(default=2, on_delete=django.db.models.deletion.DO_NOTHING, related_name='gift_donor', to='main.Donor')),
            ],
        ),
    ]
