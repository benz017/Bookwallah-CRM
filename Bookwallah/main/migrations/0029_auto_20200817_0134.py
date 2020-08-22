# Generated by Django 3.0.6 on 2020-08-17 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_recruit_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='address_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='contact_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='email_field',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='name_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='prior_exp_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='prior_experience_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='role_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='tenure_field',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='username_field',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
