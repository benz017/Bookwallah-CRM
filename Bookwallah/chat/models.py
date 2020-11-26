from django.db import models
from django.contrib.auth import get_user_model
#from main.models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
User = get_user_model()


class Room(models.Model):
    permissions = (('Open','Open Room'),('Private','Private Room'))
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=150,null=True,blank=True)
    admin = models.ForeignKey(User,null=True,blank=True,related_name='room_admin',on_delete=models.DO_NOTHING)
    permission = models.CharField(max_length=100, default='Open Room',choices=permissions)

    def __str__(self):
        return self.name


class Message(models.Model):
    author = models.ForeignKey(User,related_name='user_messages',on_delete=models.CASCADE)
    content = models.TextField()
    room = models.ForeignKey(Room, null=True, related_name='room_name', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room.name

    def last_10_messages(data):
        return Message.objects.filter(room__in=data).order_by('timestamp')