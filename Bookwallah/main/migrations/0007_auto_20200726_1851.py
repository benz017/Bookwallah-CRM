# Generated by Django 3.0.6 on 2020-07-26 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_profile_is_online'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50)),
                ('status', models.CharField(max_length=30)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=30)),
                ('dob', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='contact_person',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='donor',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='donor'),
        ),
        migrations.AlterField(
            model_name='kid',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='kid'),
        ),
        migrations.AlterField(
            model_name='session',
            name='gallery',
            field=models.ImageField(blank=True, null=True, upload_to='session'),
        ),
    ]
