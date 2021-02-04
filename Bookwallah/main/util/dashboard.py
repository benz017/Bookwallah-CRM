from ..models import *
import math
import numpy as np
from django.contrib.auth.models import User,Group
from datetime import date,datetime,timezone,timedelta
from django.db.models import Sum,Count,Max
from django.db.models.functions import Concat
from django.db.models import Value
from dateutil.relativedelta import relativedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import avinit
import json
from django.core import serializers
from django.conf import settings
from collections import defaultdict
today = date.today()
now =datetime.now()

month_dict = {1:'JAN',2: 'FEB',3: 'MAR', 4:'APR', 5:'MAY', 6:'JUN', 7:'JUL',8: 'AUG', 9:'SEP', 10:'OCT', 11:'NOV', 12:'DEC'}

def do_geocode(address, attempt=1, max_attempts=5):
    geolocator = Nominatim(user_agent="http")
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        raise




def key_detail(data,arg=None):
    if Project.objects.exists():
        p_details = {}
        p_details['project_name'] = arg.values_list('project_name',flat=True)[0]
        p_details['description'] = arg.values_list('description', flat=True)[0]
        p_details['contact_number'] = arg.values_list('contact_number',flat=True)[0]
        p_details['address'] = arg.values_list('address',flat=True)[0]
        p_details['image'] = arg.values_list('image',flat=True)[0]
        data['p_details'] = p_details
    else:
        data['p_details'] = ""
    return data

def get_month_range(c):
    month_list = []
    #print(c)
    if c != 1:
        for i in range(1,13):
            month_list.append(c)
            if c==12:
                c=1
            else:
                c+=1
        md = [month_dict[i] for i in month_list]
        print('test',c,month_list,md)
        return month_list,md
    else:
        md = [month_dict[i] for i in range(1,13)]
        return range(1,13),md


def get_year(con,i,year):
    if con[0] != 1:
        if i < con[0]:
            print(int(year)+1)
            return int(year)+1
        else:
            print(year)
            return year
    else:
        return year


def get_year_dict(c,year):
    y_d = {}
    for i in c:
        y_d[i] = get_year(c,i,year)
    return y_d


def monthly_session(data,con,p=None,year=None):
    data['months'] = []
    #print(config)
    print(1111,con,p,year)
    for i in con:
        if p is None:
            if year is None:
                c = Session.objects.filter(date__year=get_year(con,i,today.year),date__month=i).count()

            else:
                c = Session.objects.filter(date__year=get_year(con,i,year), date__month=i).count()
        else:
            if year is None:
                c = Session.objects.filter(project__in=p,date__year=today.year,date__month=i).count()

            else:
                c = Session.objects.filter(project__in=p,date__year=year, date__month=i).count()
        data['months'].append(c)

    return data


def session_prog(data,con, p=None,year=None):

    all = past = 0
    print(data,con, p,year)
    if p is None:
        if year is None:
            for k,v in get_year_dict(con, today.year).items():
                all += Session.objects.filter(date__year=v,date__month=k).count()
                past += Session.objects.filter(date__year=v,date__month=k,date__lte=today,cancellation_reason=None).count()
        else:
            for k,v in get_year_dict(con, year).items():
                all += Session.objects.filter(date__year=v,date__month=k).count()
                past += Session.objects.filter(date__year=v,date__month=k,date__lte=today,cancellation_reason=None).count()
    else:
        if year is None:
            for k, v in get_year_dict(con, today.year).items():
                all += Session.objects.filter(project__in=p,date__year=v,date__month=k).count()
                past += Session.objects.filter(project__in=p,date__year=v,date__month=k,date__lte=today, cancellation_reason=None).count()
        else:
            for k, v in get_year_dict(con, year).items():
                all += Session.objects.filter(project__in=p,date__year=v,date__month=k).count()
                past += Session.objects.filter(project__in=p,date__year=v,date__month=k,date__lte=today, cancellation_reason=None).count()
                print(2,all,past)
    try:
        print(all,past)
        data['ses_p'] = round((past/all)*100,1)
        data['ses_p_data'] = [past,all-past]
    except ZeroDivisionError:
        data['ses_p'] = 0
        data['ses_p_data'] = [0, 0]
    return data


def vol_attendance(data,con,p=None,year=None):
    all = att = 0
    if p is None:
        if year is None:
            pid = Profile.objects.filter(user__groups__name="Volunteer")

            for p in pid:
                for k, v in get_year_dict(con, today.year).items():
                    all +=Session.objects.filter(date__year=v,date__month=k,project=p.project).count()
            for k, v in get_year_dict(con, today.year).items():
                att += Attendance.objects.filter(session__date__year=v,session__date__month=k,attendance_approved=True).count()
            print(all,att)
        else:
            pid = Profile.objects.filter(user__groups__name="Volunteer")
            all = 0
            for p in pid:
                for k, v in get_year_dict(con, year).items():
                    all += Session.objects.filter(project=p.project,date__year=v, date__month=k,).count()
            for k, v in get_year_dict(con, year).items():
                att += Attendance.objects.filter(session__date__year=v, session__date__month=k,
                                                 attendance_approved=True).count()
    else:
        print(p)
        if year is None:
            pid = Profile.objects.filter(user__groups__name="Volunteer",project__in=p)
            pi = pid.count()
            for k, v in get_year_dict(con, today.year).items():
                c = Session.objects.filter(date__year=v, date__month=k,project__in=pid.values_list('project'))
                all += pi*c.count()
                att += Attendance.objects.filter(session__date__year=v, session__date__month=k,attendance_approved=True,session__in=c).count()
        else:
            pid = Profile.objects.filter(user__groups__name="Volunteer", project__in=p)
            pi = pid.count()
            for k, v in get_year_dict(con, year).items():
                c = Session.objects.filter(date__year=v, date__month=k,project__in=pid.values_list('project'))
                all += pi*c.count()
                att += Attendance.objects.filter(session__date__year=v, session__date__month=k,attendance_approved=True,session__in=c).count()

    try:
        data['vol_att'] = int((att/(all))*100)
        data['vol_att_data'] = [att,all-att]
    except ZeroDivisionError:
        data['vol_att'] = 0
        data['vol_att_data'] = [0, 0]
    return data


#def child_attendance(data):#
#    all = Session.objects.all().count()
#    att = Attendance.objects.filter(attendance_approved=True).count()
#    data['vol_att'] = (att/all)*100
#    return data


def total_revenue(data,con,year=None):
    total = Donation.objects.aggregate(Sum('amount'))
    don_list = []
    if year is None:
        for i in con:
            amt = Donation.objects.filter(date__year=get_year(con,i,today.year),date__month=i).aggregate(Sum('amount'))
            don_list.append(amt['amount__sum'])
    else:
        for i in con:
            amt = Donation.objects.filter(date__year=get_year(con,i,year),date__month=i).aggregate(Sum('amount'))
            don_list.append(amt['amount__sum'])

    data['m_rev'] = [0 if i is None else i for i in don_list]
    data['t_rev'] = total['amount__sum']
    return data


def total_expense(data,con,p=None,year=None):
    total=0
    if p is None:
        if year is None:
            for k, v in get_year_dict(con, today.year).items():
                t = Expense.objects.filter(date__year=v,date__month=k).aggregate(Sum('reimbursement_amount'))['reimbursement_amount__sum'] or 0
                total += t
            exp_list = []
            for i in con:
                amt = Expense.objects.filter(date__year=get_year(con,i,today.year),date__month=i).aggregate(Sum('reimbursement_amount'))
                exp_list.append(amt['reimbursement_amount__sum'])
        else:
            for k, v in get_year_dict(con, year).items():
                t = Expense.objects.filter(date__year=v, date__month=k).aggregate(Sum('reimbursement_amount'))[
                    'reimbursement_amount__sum']  or 0
                total += t
            exp_list = []
            for i in con:
                amt = Expense.objects.filter(date__year=get_year(con, i, year), date__month=i).aggregate(
                    Sum('reimbursement_amount'))
                exp_list.append(amt['reimbursement_amount__sum'])
    else:
        if year is None:
            for k, v in get_year_dict(con, today.year).items():
                t = Expense.objects.filter(project__in=p,date__year=v,date__month=k).aggregate(Sum('reimbursement_amount'))['reimbursement_amount__sum'] or 0
                total += t
            exp_list = []
            for i in con:
                amt = Expense.objects.filter(project__in=p,date__year=get_year(con,i,today.year),date__month=i).aggregate(Sum('reimbursement_amount'))
                exp_list.append(amt['reimbursement_amount__sum'])
        else:
            for k, v in get_year_dict(con, year).items():
                t = Expense.objects.filter(project__in=p,date__year=v,date__month=k).aggregate(Sum('reimbursement_amount'))['reimbursement_amount__sum']  or 0
                total += t
            exp_list = []
            for i in con:
                amt = Expense.objects.filter(project__in=p,date__year=get_year(con,i,year),date__month=i).aggregate(Sum('reimbursement_amount'))
                exp_list.append(amt['reimbursement_amount__sum'])
    data['m_exp'] = [0 if i is None else i for i in exp_list]
    data['t_exp'] = total
    return data


def expense_type(data,con,p=None,year=None):
    if p is None:
        if year is None:
            exp = Expense.objects.filter(date__year=today.year).values('expense_type').order_by('expense_type').annotate(sum=Sum('reimbursement_amount'))
        else:
            exp = Expense.objects.filter(date__year=year).values('expense_type').order_by('expense_type').annotate(
                sum=Sum('reimbursement_amount'))
    else:
        if year is None:
            exp = Expense.objects.filter(project__in=p,date__year=today.year).values('expense_type').order_by('expense_type').annotate(sum=Sum('reimbursement_amount'))
            print(exp)
        else:
            exp = Expense.objects.filter(project__in=p,date__year=year).values('expense_type').order_by('expense_type').annotate(
                sum=Sum('reimbursement_amount'))
    data['e_sum'] = [int(i) for i in list(exp.values_list('sum', flat=True))]
    data['ex_type'] = json.dumps(list(exp.values_list('expense_type', flat=True)))
    return data


def no_of_kids(data,con,p=None,year=None):
    if p is None:
        if year is None:
            k = Kid.objects.all().count()
            nk = Kid.objects.filter(date__month__gte=today.month-1,date__month__lte=today.month).count()
        else:
            k = Kid.objects.filter(date__year__lte=year).count()
            nk = Kid.objects.filter(date__year=year).count()
    else:
        if year is None:
            k = Kid.objects.filter(project__in=p).count()
            nk = Kid.objects.filter(project__in=p,date__month__gte=today.month - 1, date__month__lte=today.month).count()
        else:
            k = Kid.objects.filter(project__in=p,date__year__lte=year).count()
            nk = Kid.objects.filter(project__in=p, date__year=year).count()
    print(k,nk,data)
    data['no_k'] = k
    data['no_nk'] = nk
    return data


def kid_stats(data,con,p=None,year=None):
    if p is None:
        c = Kid.objects.values('age').order_by('age').annotate(count=Count('age'))
        print(c)
        data['k_m'] = Kid.objects.filter(gender='Male').count()
        data['k_f'] = Kid.objects.filter(gender='Female').count()
    else:
        c = Kid.objects.filter(project__in=p).values('age').order_by('age').annotate(count=Count('age'))
        data['k_m'] = Kid.objects.filter(project__in=p,gender='Male').count()
        data['k_f'] = Kid.objects.filter(project__in=p,gender='Female').count()
    data['k_stat'] = list(c.values_list('count',flat=True))
    print(list(c.values_list('age', flat=True)))
    k_stat_label = [int(i) for i in list(c.values_list('age', flat=True)) if i is not None]
    #print(k_stat_label)
    data['k_stat_label'] = [] if k_stat_label == [None] else k_stat_label
    return data


def kid_years(data,con,p=None,year=None):
    ky = []
    if p is None:
        for i in range(1,6):
            c = Kid.objects.filter(attending_sessions=True,date__lte=datetime.now()-relativedelta(years=i)).count()
            ky.append(c)
    else:
        for i in range(1, 6):
            c = Kid.objects.filter(project__in=p,attending_sessions=True,date__lte=datetime.now() - relativedelta(years=i)).count()
            ky.append(c)
    data['k_years']=ky
    return data


def vol_role(data,p=None,year=None):
    uid = User.objects.filter(groups__name="Volunteer")
    if p is None:
        c = Profile.objects.filter(user__in=uid).values('role').order_by('role').annotate(count=Count('role'))
    else:
        c = Profile.objects.filter(project__in=p,user__in=uid).values('role').order_by('role').annotate(count=Count('role'))
    data['v_role'] = list(c.values_list('count',flat=True))
    data['v_role_label'] = list(c.values_list('role', flat=True))
    return data


def no_story_teller(data):
    uid = User.objects.filter(groups__name="Volunteer")
    c = Profile.objects.filter(user__in=uid,role="Story Teller").values('project__project_name').order_by('project').annotate(count=Count('role'))
    data['v_st'] = list(c.values_list('count',flat=True))
    data['v_st_label'] = list(c.values_list('project__project_name', flat=True))
    return data


def session_galery(data,x=0,y=12):
    p = Session.objects.all().values_list('image',flat=True)
    sli = list(p)[x:y]
    data["ses_gal"] = [settings.MEDIA_URL + av for av in sli]

    return data


def kid_galery(data,k=None,x=0,y=12):
    data["kid_gal"] = []
    if k is None:
        p = Kid.objects.all().exclude(image='').exclude(image__isnull=True).values_list('image',flat=True)
        print(1,p)
        sli = list(p)[x:y]
        data["kid_gal"] = [settings.MEDIA_URL + av for av in sli]
    else:
        p = Kid_Picture.objects.filter(kid__in=k).exclude(image='').exclude(image__isnull=True).values_list('image',flat=True)
        print(2,p)
        sli = list(p)[x:y]
        data["kid_gal"] = [settings.MEDIA_URL + av for av in sli]
    length = list(range(1, int(math.ceil(len(data["kid_gal"]) / 3)) + 1))
    row_list = []
    for i in length:
        l = len(data["kid_gal"])
        le = math.ceil(l / 3)
        # print(ilist,l,math.ceil(le),type(len(ilist)))

        if i == le:
            ar = np.arange((i - 1) * 3, l).tolist()
        else:
            ar = np.arange((i - 1) * 3, i * 3).tolist()
        row_list.append(ar)
    data['row_list'] = row_list
    return data


def child_attendance(data,con,p=None,year=None,k=None):
    all = att = 0
    if k is None:
        if p is None:
            if year is None:
                kid = Kid.objects.all().values_list('project')

                for p in kid:
                    for k, v in get_year_dict(con, today.year).items():
                        all += Session.objects.filter(date__year=v, date__month=k, project=p).count()
                for k, v in get_year_dict(con, today.year).items():
                    att += Kid_Attendance.objects.filter(session__date__year=v, session__date__month=k,
                                                     attendance=True).count()
                print(all, att)
            else:
                kid = Kid.objects.all().values_list('project')
                all = 0
                for p in kid:
                    for k, v in get_year_dict(con, year).items():
                        all += Session.objects.filter(project=p.project, date__year=v, date__month=k, ).count()
                for k, v in get_year_dict(con, year).items():
                    att += Kid_Attendance.objects.filter(session__date__year=v, session__date__month=k,
                                                         attendance=True).count()
        else:
            print(p)
            if year is None:
                kid = Kid.objects.filter(project__in=p)
                pi = kid.count()
                for k, v in get_year_dict(con, today.year).items():
                    c = Session.objects.filter(date__year=v, date__month=k, project__in=kid.values_list('project'))
                    all += pi * c.count()
                    att += Kid_Attendance.objects.filter(session__date__year=v, session__date__month=k,
                                                         attendance=True, session__in=c).count()
            else:
                pid = Profile.objects.filter(user__groups__name="Volunteer", project__in=p)
                pi = pid.count()
                for k, v in get_year_dict(con, year).items():
                    c = Session.objects.filter(date__year=v, date__month=k, project__in=pid.values_list('project'))
                    all += pi * c.count()
                    att += Kid_Attendance.objects.filter(session__date__year=v, session__date__month=k,
                                                         attendance=True, session__in=c).count()
    else:
        p = Kid.objects.filter(pk=k).values_list('project',flat=True)[0]
        print(12,p, k)
        if year is None:
            all = Session.objects.filter(date__year=today.year, project=p).count()
            att = Kid_Attendance.objects.filter(kid=k,session__date__year=today.year,
                                              attendance=True).count()
            print(all, att)
        else:
            all = Session.objects.filter(project=p, date__year=year, ).count()
            att = Kid_Attendance.objects.filter(kid=k, session__date__year=year,
                                                     attendance=True).count()

    try:
        data['c_att'] = int((att/(all))*100)
        data['c_att_data'] = [att,all-att]
    except ZeroDivisionError:
        data['c_att'] = 0
        data['c_att_data'] = [0, 0]
    return data


def kid_session_history(data,k,year=None):
    h = Kid_Attendance.objects.filter(kid=k, session__date__year=today.year,
                                        attendance=True)
    date = h.values_list('session__date',flat=True)
    bn = h.values_list('session__book_name', flat=True)
    sv = h.values_list('session__story_value', flat=True)
    d = dict(zip(list(date), list(bn)))
    sh = defaultdict(list)
    for s in sv:
        for k,v in d.items():
            k = k.strftime('%d %b %I:%M %p')
            sh[k].append(s)
            sh[k].append(v)
    data['ksh'] = dict(sh)
    return data

def kid_bday(data):
    try:
        b = Kid.objects.filter(dob__day__gte=today.day,dob__month=today.month).annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        dl = b.values_list('dob',flat=True)
        name = b.values_list('fullname',flat=True)
        av = b.values_list('image',flat=True)
        d = dict(zip(list(name),list(dl)))
        bday_dict = defaultdict(list)
        for a in list(av):
            if a == "" and b:
                for k,v in d.items():
                    bday_dict[k].append(avinit.get_image_data_url(k))
                    bday_dict[k].append(datetime.strftime(v,"%d %b"))
        data['k_bday'] = dict(bday_dict)
    except Exception as ex:
        print(str(ex))
    return data



def mem_ani(data):
    try:
        b = Kid.objects.filter(date__year__lte=today.year, date__month=today.month,date__day__gte=today.day).annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        dl = b.values_list('date', flat=True)
        name = b.values_list('fullname', flat=True)
        av = b.values_list('image', flat=True)
        d = dict(zip(list(name), list(dl)))
        mem_list = defaultdict(list)
        for a in list(av):
            if a == "" and b:
                for k,v in d.items():
                    mem_list[k].append(avinit.get_image_data_url(k))
                    mem_list[k].append(datetime.strftime(v,"%d %b"))
        data['k_mem'] = dict(mem_list)
    except Exception as ex:
        print(str(ex))
    return data


def volunteer_list(data,p=None,year=None):
    uid = User.objects.filter(groups__name="Volunteer")
    if p is None:
        b = Profile.objects.filter(user__in=uid).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    else:
        b = Profile.objects.filter(project__in=p,user__in=uid).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    dl = b.values_list('role', flat=True)
    name = b.values_list('fullname', flat=True)
    av = b.values_list('image', flat=True)
    d = dict(zip(list(name), list(dl)))
    v_list = defaultdict(list)

    for i, (k, v) in enumerate(d.items()):
        if list(av)[i] == "":
            v_list[k].append(avinit.get_image_data_url(k))
        else:
            v_list[k].append(settings.MEDIA_URL+list(av)[i])
        v_list[k].append(v)
    print(v_list)
    data['v_list'] = dict(v_list)
    return data


def vol_bday(data,p=None,year=None):
    uid = User.objects.filter(groups__name="Volunteer")
    if p is None:
        b = Profile.objects.filter(user__in=uid,dob__day__gte=today.day,dob__month=today.month).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    else:
        b = Profile.objects.filter(project__in=p,user__in=uid, dob__day__gte=today.day, dob__month=today.month).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    dl = b.values_list('dob',flat=True)
    name = b.values_list('fullname',flat=True)
    av = b.values_list('image',flat=True)
    d = dict(zip(list(name),list(dl)))
    bday_dict = defaultdict(list)
    for a in list(av):
        if a == "":
            for k,v in d.items():
                bday_dict[k].append(avinit.get_image_data_url(k))
                bday_dict[k].append(datetime.strftime(v,"%d %b"))
        else:
            for k,v in d.items():
                bday_dict[k].append(settings.MEDIA_URL+a)
                bday_dict[k].append(datetime.strftime(v,"%d %b"))
    data['v_bday'] = dict(bday_dict)
    return data


def vol_ani(data,p=None,year=None):
    uid = User.objects.filter(groups__name="Volunteer")
    if p is None:
        b = Profile.objects.filter(user__in=uid, user__date_joined__month=today.month,user__date_joined__day__gte=today.day).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    else:
        b = Profile.objects.filter(project__in=p,user__in=uid, user__date_joined__month=today.month,user__date_joined__day__gte=today.day).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    dl = b.values_list('user__date_joined', flat=True)
    name = b.values_list('fullname', flat=True)
    av = b.values_list('image', flat=True)
    d = dict(zip(list(name), list(dl)))
    mem_list = defaultdict(list)
    for a in list(av):
        if a == "":
            for k,v in d.items():
                mem_list[k].append(avinit.get_image_data_url(k))
                mem_list[k].append(datetime.strftime(v,"%d %b"))
        else:
            for k,v in d.items():
                mem_list[k].append(settings.MEDIA_URL+a)
                mem_list[k].append(datetime.strftime(v,"%d %b"))
    data['v_mem'] = dict(mem_list)
    return data


def don_by_year(data,don='',year=''):
    dy_list = []
    d_list = []
    print(year)
    if don is '' or don is None:
        if Donation.objects.exists():
            d = Donation.objects.all().order_by("date").values_list('date__year')[0][0]
            if year is '' or year is None:
                for i in range(d,today.year+1):
                    d = Donation.objects.filter(date__year=i).aggregate(Sum('amount'))
                    dy_list.append(i)
                    d_list.append(d['amount__sum'])
                data["dy_list"] = dy_list
                data["d_list"] = [0 if i is None else i for i in d_list]
            else:
                for i in range(1, 13):
                    amt = Donation.objects.filter(date__year=year, date__month=i).aggregate(Sum('amount'))
                    d_list.append(amt['amount__sum'])
                d_list = [0 if i is None else i for i in d_list]
                data["dy_list"] = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
                data['d_list'] = [0 if i is None else i for i in d_list]
                data['year'] = year
    else:
        if Donation.objects.exists():
            d = Donation.objects.filter(donated_by__in=don).order_by("date").values_list('date__year')[0][0]
            for i in range(d, today.year + 1):
                d = Donation.objects.filter(donated_by__in=don,date__year=i).aggregate(Sum('amount'))
                dy_list.append(i)
                d_list.append(d['amount__sum'])
            data["dy_list"] = dy_list
            data["d_list"] = [0 if i is None else i for i in d_list]
    if year is '' or year is None:
        data['year'] = today.year
    else:
        data['year'] = year
    return data


def monthly_donation(data,d='',year=''):
    don_list = []
    if year is '':
        year= today.year
    if d == '':
        for i in range(1,13):
            amt = Donation.objects.filter(date__year=year,date__month=i).aggregate(Sum('amount'))
            don_list.append(amt['amount__sum'])
    else:
        for i in range(1,13):
            amt = Donation.objects.filter(donated_by__in=d,date__year=year,date__month=i).aggregate(Sum('amount'))
            don_list.append(amt['amount__sum'])
    don_list = [0 if i is None else i for i in don_list]
    data['m_don'] = don_list
    data['d_year'] = year
    return data


def don_nation(data,p=None,year=None):
    if p is None:
        c = Donor.objects.all().values('nationality').order_by('nationality').annotate(count=Count('nationality'))
    else:
        c = Donor.objects.filter(project__in=p).values('nationality').order_by('nationality').annotate(count=Count('nationality'))
    data['d_nat'] = list(c.values_list('count',flat=True))
    data['d_nat_label'] = list(c.values_list('nationality', flat=True))
    return data


def don_country(data,p=None,year=None):
    if p is None:
        c = Donor.objects.all().values('country').order_by('country').annotate(count=Count('country'))
    else:
        c = Donor.objects.filter(project__in=p).values('country').order_by('country').annotate(count=Count('country'))
    data['d_con'] = list(c.values_list('count',flat=True))
    data['d_con_label'] = list(c.values_list('country', flat=True))
    return data


def total_donation(data,d=''):
    if d != '':
        amt = Donation.objects.filter(donated_by__in=d).aggregate(Sum('amount'))
        data['total_don'] = amt['amount__sum']
    return data


def nps_score(data,con,c=None,year=None):
    ds = [{
            'label': "Q1",
            'data': []
        },
        {
            'label': "Q2",
            'data': []
        },
        {
            'label': "Q3",
            'data': []
        }]
    try:
        if year is None:
            year = list(range(today.year - 2, today.year + 1))
            if c is None:
                for i in year:
                    q1 = list(NPSScore.objects.filter(year=i,quarter='Q1').values_list('score',flat=True))
                    q2 = list(NPSScore.objects.filter(year=i, quarter='Q2').values_list('score',flat=True))
                    q3 = list(NPSScore.objects.filter(year=i, quarter='Q3').values_list('score',flat=True))
                    q1 = sum(q1)/len(q1)
                    q2 = sum(q2) / len(q2)
                    q3 = sum(q3) / len(q3)
                    ds[0]['data'].append(q1)
                    ds[1]['data'].append(q2)
                    ds[2]['data'].append(q3)
        else:
            year = list(range(year - 2, year + 1))
            if c is None:
                for i in year:
                    q1 = list(NPSScore.objects.filter(year=i,quarter='Q1').values_list('score',flat=True))
                    q2 = list(NPSScore.objects.filter(year=i, quarter='Q2').values_list('score',flat=True))
                    q3 = list(NPSScore.objects.filter(year=i, quarter='Q3').values_list('score',flat=True))
                    q1 = sum(q1)/len(q1)
                    q2 = sum(q2) / len(q2)
                    q3 = sum(q3) / len(q3)
                    ds[0]['data'].append(q1)
                    ds[1]['data'].append(q2)
                    ds[2]['data'].append(q3)

        data['nps_data'] = json.dumps(ds)
        data['nps_label'] = year
    except Exception as ex:
        data['nps_data'] =[]
        data['nps_label'] =[]
        print(ex)
    return data


def child_psychology(data,con,p=None,year=None):
    label = ["Empathy","Hope","Perseverance","Social Conduct"]
    ds = []
    if p is None:
        if year is None:
            for i in range(1,4):
                e = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q'+str(i)).values_list('empathy', flat=True))
                h = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('hope', flat=True))
                p = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('perseverance', flat=True))
                s = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('pro_social_conduct', flat=True))
                if e or h or p or s:
                    ds.append({'label': "Q"+str(i),'data': [e[0],h[0],p[0],s[0]]})

        else:
            for i in range(1,4):
                e = list(ChildPsychologyScore.objects.filter(year=year, quarter='Q'+str(i)).values_list('empathy', flat=True))
                h = list(ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i)).values_list('hope', flat=True))
                p = list(ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i)).values_list('perseverance', flat=True))
                s = list(ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i)).values_list('pro_social_conduct', flat=True))
                if e or h or p or s:
                    ds.append({'label': "Q"+str(i),'data': [e[0],h[0],p[0],s[0]]})
    else:
        if year is None:
            for i in range(1, 4):
                e = list(
                    ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('empathy',
                                                                                                           flat=True))
                h = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('hope',
                                                                                                                flat=True))
                p = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list(
                    'perseverance', flat=True))
                s = list(ChildPsychologyScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list(
                    'pro_social_conduct', flat=True))
                if e or h or p or s:
                    ds.append({'label': "Q" + str(i), 'data': [e[0], h[0], p[0], s[0]]})

        else:
            for i in range(1, 4):
                e = list(ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i),project__in=p).values_list('empathy',
                                                                                                          flat=True))
                h = list(
                    ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i),project__in=p).values_list('hope', flat=True))
                p = list(
                    ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i),project__in=p).values_list('perseverance',
                                                                                                     flat=True))
                s = list(ChildPsychologyScore.objects.filter(year=year, quarter='Q' + str(i),project__in=p).values_list(
                    'pro_social_conduct', flat=True))
                if e or h or p or s:
                    ds.append({'label': "Q" + str(i), 'data': [e[0], h[0], p[0], s[0]]})
    data['cp_data'] = json.dumps(ds)
    data['cp_label'] = label
    return data


def social_behavior(data,con,p=None,year=None):
    label = ["Control", "Treatment"]
    ds = []
    if p is None:
        if year is None:
            for i in range(1, 3):
                c = list(ProSocialBehaviorScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('control', flat=True))
                t = list(ProSocialBehaviorScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('treatment', flat=True))

                if c or t:
                    ds.append({'label': "Q" + str(i), 'data': [c[0], t[0]]})
        else:
            for i in range(1, 3):
                c = list(ProSocialBehaviorScore.objects.filter(year=year, quarter='Q' + str(i)).values_list('control',
                                                                                                            flat=True))
                t = list(ProSocialBehaviorScore.objects.filter(year=year, quarter='Q' + str(i)).values_list('treatment',
                                                                                                            flat=True))
                if c or t:
                    ds.append({'label': "Q" + str(i), 'data': [c[0], t[0]]})
    else:
        if year is None:
            for i in range(1, 3):
                c = list(
                    ProSocialBehaviorScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list('control',
                                                                                                             flat=True))
                t = list(ProSocialBehaviorScore.objects.filter(year=today.year, quarter='Q' + str(i)).values_list(
                    'treatment', flat=True))

                if c or t:
                    ds.append({'label': "Q" + str(i), 'data': [c[0], t[0]]})
        else:
            for i in range(1, 3):
                c = list(ProSocialBehaviorScore.objects.filter(year=year, quarter='Q' + str(i),project__in=p).values_list('control',
                                                                                                            flat=True))
                t = list(ProSocialBehaviorScore.objects.filter(year=year, quarter='Q' + str(i),project__in=p).values_list('treatment',
                                                                                                            flat=True))
                if c or t:
                    ds.append({'label': "Q" + str(i), 'data': [c[0], t[0]]})
    data['sb_data'] = json.dumps(ds)
    data['sb_label'] = label
    return data


def email_history( id):
    data={}
    from .mail import get_email
    eh = get_email(id)
    print(eh)
    data["e_history"] = eh
    return data



def total_applications(data,year=None):
    if year is None:
       t = Recruit.objects.filter(timestamp__year=today.year).count()
       m = Recruit.objects.filter(timestamp__year=today.year,timestamp__month=today.month).count()
    else:
        t = Recruit.objects.filter(timestamp__year=year).count()
        m = Recruit.objects.filter(timestamp__year=year, timestamp__month=today.month).count()
    data['t_app'] = t
    data['m_app'] = m
    return data

def pending_applications(data,year=None):
    if year is None:
       p= Recruit.objects.filter(timestamp__year=today.year,status="Pending")
       t = p.count()
       m = Recruit.objects.filter(timestamp__year=today.year,timestamp__month=today.month,status="Pending").count()
    else:
        p = Recruit.objects.filter(timestamp__year=year,status="Pending")
        t = p.count()
        m = Recruit.objects.filter(timestamp__year=year, timestamp__month=today.month,status="Pending").count()
    p_list = serializers.serialize('json', list(p))
    data['pt_app'] = t
    data['pm_app'] = m
    data['p_list'] = json.loads(p_list)
    return data


def in_process_applications(data,year=None):
    if year is None:
       i = Recruit.objects.filter(timestamp__year=today.year,status="In-Process")
       t = i.count()
       m = Recruit.objects.filter(timestamp__year=today.year,timestamp__month=today.month,status="In-Process").count()
    else:
        i= Recruit.objects.filter(timestamp__year=year,status="In-Process")
        t = i.count()
        m = Recruit.objects.filter(timestamp__year=year, timestamp__month=today.month,status="In-Process").count()
    i_list = serializers.serialize('json', list(i))
    data['i_list'] = json.loads(i_list)
    data['it_app'] = t
    data['im_app'] = m
    return data

def approved_applications(data,year=None):
    if year is None:
       t = Recruit.objects.filter(timestamp__year=today.year,status="Approved").count()
       m = Recruit.objects.filter(timestamp__year=today.year,timestamp__month=today.month,status="Approved").count()
    else:
        t = Recruit.objects.filter(timestamp__year=year,status="Approved").count()
        m = Recruit.objects.filter(timestamp__year=year, timestamp__month=today.month,status="Approved").count()
    data['at_app'] = t
    data['am_app'] = m
    return data


def rec_role(data,year=None):
    if year is None:
        c = Recruit.objects.filter(timestamp__year=today.year).values('role').order_by('role').annotate(count=Count('role'))
    else:
        c = Recruit.objects.filter(timestamp__year=year).values('role').order_by('role').annotate(count=Count('role'))
    data['r_role'] = list(c.values_list('count',flat=True))
    data['r_role_label'] = list(c.values_list('role', flat=True))
    return data

def assigned_donor_tasks(data,donor):
    at = Task.objects.filter(assigned_for=donor.values_list('id',flat=True)[0],date__month__in=[today.month,today.month+1],date__year=today.year,type='Donor').annotate(
                    fullname=Concat('user__user__first_name', Value(' '), 'user__user__last_name'))
    date = [dt.date() for dt in at.values_list('date', flat=True)]
    task = at.values_list('task', flat=True)
    assigned_to = at.values_list('fullname', flat=True)
    status = at.values_list('status', flat=True)

    data.update({'date':list(date),'task':list(task),'assigned_to':list(assigned_to),'status':list(status)})
    return data

def upcoming_tasks(data):
    ut = Task.objects.filter(date__gte=today,date__month__in=[today.month,today.month+1],date__year=today.year,type='Donor')
    data['up_tasks'] = list(ut)
    return data

def upcoming_pledges(data):
    up = Pledge.objects.filter(date__gte=today,date__month__in=[today.month,today.month+1],date__year=today.year)
    data['up_pledge'] = list(up)
    return data


def gifts(data,id):
    g = Gift.objects.filter(donor__in=id)
    ig= list(g.values_list("item",flat=True))
    iv = list(g.values_list("value",flat=True))
    r = dict(zip(ig,iv))
    data['gik']= r
    return data


def top_vol(data):
    v = Config.objects.all().values_list('top_volunteer',flat=True)[0]
    if v is not None:
        p = Profile.objects.filter(pk=v).annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
        jy = p.values_list('user__date_joined__year',flat=True)[0]
        av = p.values_list('image',flat=True)[0]
        a = Attendance.objects.filter(user__in=p,attendance_approved=True).count()
        data["tv_na"] = p.values_list('fullname',flat=True)[0]
        data["tv_jy"] = jy
        data["tv_av"] = settings.MEDIA_URL +av
        data["tv_hrs"] = a*8
    return data


def top_kid(data):
    v = Config.objects.all().values_list('top_kid',flat=True)[0]
    if v is not None:
        p = Kid.objects.filter(pk=v).annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        na = p.values_list('fullname',flat=True)[0]
        jy = p.values_list('date__year',flat=True)[0]
        av = p.values_list('image',flat=True)[0]
        a = Kid_Attendance.objects.filter(kid__in=p,attendance=True).count()
        data["tk_na"] = na
        data["tk_jy"] = jy
        data["tk_av"] = settings.MEDIA_URL +av
        data["tk_count"] = a
    return data


def regular_vol(data):
    #p = Profile.objects.filter(user__groups_name="Volunteer").annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name'))
    a = Attendance.objects.filter(attendance_approved=True).annotate(total=Count('pk')).aggregate(
        max=Max('total'))
    print(a)


def highlight(data,f,y=None,field = None):
    if field == 'Project' or field is None:
        if y is None:
            h = list(Highlight.objects.filter(project__in=f.values_list('project_name',flat=True),date__year=today.year).values())
            i = list(Issues.objects.filter(project__in=f.values_list('project_name',flat=True),date__year=today.year).values())
        else:
            h = list(Highlight.objects.filter(project__in=f.values_list('project_name', flat=True),date__year=y).values())
            i = list(Issues.objects.filter(project__in=f.values_list('project_name', flat=True),date__year=y).values())

    elif field == 'Chapter':
        if y is None:
            h = list(Highlight.objects.filter(project__in=f.values_list('project_name',flat=True),date__year=today.year,priority=True).values())
            i = list(Issues.objects.filter(project__in=f.values_list('project_name',flat=True),date__year=today.year,priority=True).values())
        else:
            h = list(Highlight.objects.filter(project__in=f.values_list('project_name', flat=True),date__year=y,priority=True).values())
            i = list(Issues.objects.filter(project__in=f.values_list('project_name', flat=True),date__year=y,priority=True).values())
    elif field == 'Country':
        if y is None:
            h = list(Highlight.objects.filter(project__in=f.values_list('project_name',flat=True),date__year=today.year,priority=True).values())
            i = list(Issues.objects.filter(project__in=f.values_list('project_name',flat=True),date__year=today.year,priority=True).values())
        else:
            h = list(Highlight.objects.filter(project__in=f.values_list('project_name', flat=True),date__year=y,priority=True).values())
            i = list(Issues.objects.filter(project__in=f.values_list('project_name', flat=True),date__year=y,priority=True).values())
    print(h,i)
    h = [x['highlight'] for x in h if x['highlight'] is not None]
    i = [x['issue'] for x in i if x['issue'] is not None]
    m = max(len(h),len(i))
    print(123,h, i, m)
    data["hi"] = h
    data["is"] = i
    data["m"] = list(range(m))
    return data


def v_testimonials(data):
    if Volunteer_Testimonial.objects.exists():
        v = Volunteer_Testimonial.objects.all().order_by('-id')[0]
        data["t_name"] = v.volunteer.user.first_name+" "+v.volunteer.user.last_name
        data["t_test"] = v.testimonial
    else:
        data["t_name"] =""
        data["t_test"] =""

    return data
def d_testimonials(data):
    if Donor_Testimonial.objects.exists():
        d = Donor_Testimonial.objects.all().order_by('-id')[0]
        data["d_name"] = d.donor.first_name+" "+d.donor.last_name
        data["d_test"] = d.testimonial
    else:
        data["d_name"] =""
        data["d_test"] =""
    return data

def team_strength(data):
    p= Project.objects.filter(pk=data.project)
    try:
        c = Profile.objects.filter(project=p).count()
        return c
    except:
        return "N/A"
