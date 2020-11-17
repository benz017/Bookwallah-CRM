from django import template
from datetime import datetime
from django.contrib.auth.models import Group
import math
import pytz
import numpy as np
import json
from django.forms.fields import CheckboxInput
from django.apps import apps
Profile = apps.get_model('main', 'Profile')
Message = apps.get_model('chat', 'Message')
register = template.Library()

@register.filter
def delta(date,arg):
    now = datetime.now()
    #date = date.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
    dif = date-now
    days = dif.days
    hr = date.hour
    min = date.minute
    if arg == "d":
        return days
    if arg == "-d":
        return abs(days)
    elif arg == "h":
        return hr
    elif arg == "m":
        return min


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def divide(value, arg):
    print(round(value/arg,1))
    return round(value/arg,1)


@register.filter
def mult(value, arg):
    return round(value*arg,1)

@register.filter
def percent(value, arg):
    return int((value/arg)*100)


@register.filter
def convert(value,arg):
    return int(value)


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.filter(name=group_name)
    if group:
        group = group.first()
        return group in user.groups.all()
    else:
        return False


@register.filter(name='nothas_group')
def nothas_group(user, group_name):
    group = Group.objects.get(name=group_name)
    if user.groups.first() != group:
        return True
    else:
        return False

@register.filter(name='members')
def members(room,arg):
    if arg == "Private":
        m = Profile.objects.filter(chat_room=room).count()
        return m
    else:
        m = Profile.objects.all().count()
        return m

@register.filter(name='last_activity')
def last_activity(room):
    if Message.objects.filter(room=room).exists():
        date = Message.objects.filter(room=room).order_by('-timestamp').values_list('timestamp',flat=True)[0]
        now = datetime.now()
        # date = date.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
        dif = now - date
        days = dif.days
        hr = dif.total_seconds()/3600
        min = dif.total_seconds()/60
        if min < 60:
            return str(int(min)) + "min(s) ago"
        elif hr < 24:
            m = (hr-int(hr))*60
            if m == 0:
                return str(int(hr)) + "hr(s) ago"
            else:
                return str(int(hr)) + "hr(s) " +str(int(m)) + "min(s) ago"
        else:
            h = (days - int(days)) * 24
            m = (h - int(h)) * 60
            if h == 0 and m==0:
                return str(int(days)) + "day(s) ago"
            elif m == 0:
                return str(int(days)) + "day(s) "+str(int(m)) + "min(s) ago"
            else:
                return str(int(days)) + "day(s) "+ str(int(h)) + "hr(s)" + str(int(m)) + "min(s) ago"
    else:
        return "Never"

@register.filter(name='replace')
def replace(str,arg):
    return str.replace(arg," ")

@register.filter(name='convert_iso')
def convert_iso(str):
    import dateutil.parser
    yourdate = dateutil.parser.parse(str)
    print(yourdate)
    return yourdate

@register.filter(name='mod')
def mod(value, arg):
    mod = value%int(arg)
    return mod

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except IndexError:
        return ''


@register.filter(name='get_iter')
def get_iter(value,arg):
    if type(value) == list or type(value)==dict:
        return range(arg,len(value)+arg)
    else:
        return range(arg,value+arg)


def get_range(i, ilist):
    l = len(ilist)
    le = math.ceil(l/3)
    #print(ilist,l,math.ceil(le),type(len(ilist)))

    if i == le:
        ar = np.arange((i-1)*3, l).tolist()
    else:
        ar = np.arange((i - 1) * 3, i*3).tolist()
    return ar


def truncate_float(n, places):
    return int(n * (10 ** places)) / 10 ** places

@register.filter(name='list_min')
def list_min(data):
    data = json.loads(data)
    if data != []:
        l = [i for item in data for i in item["data"]]
        if min(l) >=0:
            return 0
        else:
            return min(l)
    else:
        return data

