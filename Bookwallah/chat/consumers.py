# chat/consumers.py
import json
from .models import Message
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.conf import settings
from django.apps import apps
from datetime import datetime
Profile = apps.get_model('main', 'Profile')
Room = apps.get_model('chat', 'Room')
# Create your models here.
User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self,data):
        print(data.get('room'))
        room = Room.objects.filter(name=data.get('room'))
        messages = Message.last_10_messages(room)
        content = {
            'command':'messages',
            'messages':self.messages_to_json(messages)
        }
        print(content)
        self.send_message(content)

    def new_message(self,data):
        author = data['from']
        author_user = User.objects.filter(username=author)[0]
        room = Room.objects.filter(name=data['room'])[0]
        message = Message.objects.create(
            author=author_user,
            content=data['message'],
            room=room)
        content = {
            'command':'new_message',
            'message':self.message_to_json(message),
        }
        return self.send_chat_message(content)

    def messages_to_json(self,messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        #print(result)
        return result

    def message_to_json(self,message):
        frm = "%I:%M %p %d-%b-%y"
        pid = Profile.objects.filter(user=message.author)
        av = pid.values_list("image", flat=True)[0]
        url = settings.MEDIA_URL + av
        msg = {'author':message.author.username,'src':url,'message':message.content,'timestamp':datetime.strftime(message.timestamp,frm)}
        #print(msg)
        return msg
    commands = {
        'fetch_messages':fetch_messages,
        'new_message':new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        print(self.room_name,self.room_group_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self,data)

    def send_chat_message(self,message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self,message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))