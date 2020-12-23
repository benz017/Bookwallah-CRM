from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.apps import apps
from django.utils.safestring import mark_safe
from .models import *
import json
from django.contrib.auth.decorators import login_required
from django.apps import apps
Profile = apps.get_model('main', 'Profile')
Room = apps.get_model('chat', 'Room')
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver



@login_required
def room(request, room_name):
    data={}
    p_room = Profile.objects.filter(user=request.user).values_list('project__project_name', flat=True)[0]
    if p_room is not None:
        data["p_room"] = p_room.replace(" ", "_")
    room= Room.objects.get(name=room_name)
    if room.permission == "Private":
        data["team_members"] = Profile.objects.order_by('-is_online').filter(chat_room=room,user__is_superuser=False).exclude(user=request.user)
    elif room.permission == "Open":
        data["team_members"] = Profile.objects.order_by('-is_online').filter(user__is_superuser=False).exclude(user=request.user)
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data['room_name_json'] = mark_safe(json.dumps(room_name))
    data['curruser'] = mark_safe(json.dumps(request.user.username))
    print(data['room_name_json'])
    return render(request, 'chat/chat_room.html', context=data)

@login_required
def lobby(request):
    data = {}
    p_room = Profile.objects.filter(user=request.user).values_list('project__project_name',flat=True)[0]
    if p_room is not None:
        data["p_room"] = p_room.replace(" ","_")
    if Room.objects.exists():
        if p_room is None:
            project_room = Room.objects.all()
            data["rooms"] = project_room
        else:
            project_room = Room.objects.filter(name=data["p_room"])
            data["rooms"] = project_room[0]
    open_room = Room.objects.filter(permission="Open").exclude(name=data["p_room"])
    if len(open_room) > 3:
        open_room = open_room[:3]
    private_room = Room.objects.filter(permission="Private",name=request.user.profile.chat_room).exclude(name=data["p_room"])
    if len(private_room) > 2:
        private_room = private_room[:2]
    data["o_users"] = Profile.objects.filter(is_online=True,user__is_superuser=False).exclude(user=request.user)
    print()
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data["open_rooms"] = open_room
    data["private_rooms"] = private_room
    return render(request,'chat/lobby.html',context=data)

@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    user.profile.is_online = True
    user.profile.save()

@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    user.profile.is_online = False
    user.profile.save()