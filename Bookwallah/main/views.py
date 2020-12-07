# ------------- External Libraries ------------- #
from .forms import LogInForm
from .models import *
from datetime import date, datetime
from .util import dashboard, gallery
from .integrations.mailchimp import *

# ------------- Django Libraries ------------ #
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
import os
from django.conf import settings
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.functions import Concat
from django.db.models import Value
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout

# Create your views here.
today = date.today()


def landing(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return redirect('signin')


@user_passes_test(lambda u: u.groups.filter(name__in=['HR Head', 'Project Lead', 'Volunteer']).count() == 0)
@login_required
@csrf_exempt
def main_dashboard(request):
    data = {}
    config = Config.objects.filter(id=1).values_list('fiscal_month', flat=True)[0]
    con, ml = dashboard.get_month_range(config)
    data["m_list"] = ml
    print('view', config, ml)
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data["config"] = config

    print(data['config'])
    y_list = []
    if Project.objects.exists():
        p = Project.objects.all().order_by("date").values_list('date__year')[0][0]
        print(today.year, p)
        for i in range(today.year, p-1, -1):
            y_list.append(i)
    data["year"] = y_list
    c = Project.objects.filter(country='India')
    print(c)
    sel_in = Project.objects.all().values_list('country', flat=True)
    data["country_list"] = list(set(sel_in))

    data = dashboard.child_attendance(data, con)
    data = dashboard.top_vol(data)
    data = dashboard.top_kid(data)
    data = dashboard.monthly_session(data, con, c)
    data = dashboard.session_prog(data, con, c)
    data = dashboard.vol_attendance(data, con, c)
    data = dashboard.total_revenue(data, con, )
    data = dashboard.total_expense(data, con, c)
    data = dashboard.kid_stats(data, con, c)
    data = dashboard.kid_years(data, con, c)
    data = dashboard.no_of_kids(data, con, c)
    data = dashboard.vol_role(data, con, c)
    data = dashboard.volunteer_list(data, c)
    data = dashboard.key_detail(data, c)
    data = dashboard.expense_type(data, con, c)
    data = dashboard.session_galery(data)
    data = dashboard.kid_galery(data)
    data = dashboard.nps_score(data, con)
    data = dashboard.child_psychology(data, con)
    data = dashboard.social_behavior(data, con)
    data = dashboard.highlight(data, c)
    data = dashboard.v_testimonials(data)
    data = dashboard.d_testimonials(data)
    print(data)
    if request.method == "POST":
        if 'fiscalv' in request.POST:
            fv = request.POST.get('fiscalv')
            ft = request.POST.get('fiscalt')
            config = Recruitment_Form_Config.objects.filter(id=1)
            config.update(fiscal_month=fv)
        elif 'select' in request.POST:
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)
            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            new_data = {}
            field = request.POST.get('field')
            val = request.POST.get('value')
            year = request.POST.get('year')
            print(field, val, Project.objects.filter(project_name=val))
            if field == 'Project':
                f = Project.objects.filter(project_name=val)
                print(f)
            elif field == 'Country':
                f = Project.objects.filter(country=val)
            elif field == 'Chapter':
                f = Project.objects.filter(state=val)
            new_data = dashboard.child_attendance(new_data, con, f, year)
            new_data = dashboard.vol_attendance(new_data, con, f, year)
            new_data = dashboard.key_detail(new_data, f)
            new_data = dashboard.session_prog(new_data, con, f, year)
            new_data = dashboard.total_expense(new_data, con, f, year)
            new_data = dashboard.kid_stats(new_data, con, f, year)
            new_data = dashboard.monthly_session(new_data, con, f, year)
            new_data = dashboard.kid_years(new_data, con, f, year)
            new_data = dashboard.no_of_kids(new_data, con, f, year)
            new_data = dashboard.volunteer_list(new_data, f)
            new_data = dashboard.expense_type(new_data, con, f, year)
            new_data = dashboard.highlight(new_data, f, year, field)
            json_stuff = json.dumps(new_data)
            print(new_data)
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'dashboard/main_dash.html', context=data)


@user_passes_test(lambda u: u.groups.filter(name__in=['HR Head', 'Project Lead', 'Volunteer']).count() == 0)
@csrf_exempt
def p_location(request):
    p = Project.objects.all()
    add = p.values_list('address', flat=True)
    city = p.values_list('city', flat=True)
    country = p.values_list('country', flat=True)
    project_name = p.values_list('project_name', flat=True)
    loc = []
    for i in range(len(p)):
        if dashboard.do_geocode(add[i]) is not None:
            addr = dashboard.do_geocode(add[i])
        else:
            addr = dashboard.do_geocode(city[i] + ", " + country[i])
        loc.append({'lat': addr.latitude, 'lon': addr.longitude, 'title': project_name[i]})

    data = json.dumps(loc)
    print(data)
    return HttpResponse(data, content_type='application/json')


@user_passes_test(lambda u: u.groups.filter(
    name__in=['President', 'R&D Head', 'Marketing Head', 'HR Head', 'Project Lead', 'Volunteer', 'Donor']).count() == 0)
@csrf_exempt
def d_location(request):
    try:
        p = Donor.objects.all().annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        add1 = p.values_list('address1', flat=True)
        add2 = p.values_list('address2', flat=True)
        print(add1, add2)
        add = [a + b if a is not None and b is not None else "" for a in add1 for b in add2]

        city = p.values_list('city', flat=True)
        country = p.values_list('country', flat=True)
        project_name = p.values_list('fullname', flat=True)
        loc = []
        for i in range(len(p)):
            if dashboard.do_geocode(add[i]) is not None:
                addr = dashboard.do_geocode(add[i])
            elif dashboard.do_geocode(city[i] + ", " + country[i]) is not None:
                addr = dashboard.do_geocode(city[i] + ", " + country[i])
            else:
                continue
            loc.append({'lat': addr.latitude, 'lon': addr.longitude, 'title': project_name[i]})

        data = json.dumps(loc)
        print(data)
        return HttpResponse(data, content_type='application/json')
    except Exception as ex:
        print(str(ex))


@user_passes_test(lambda u: u.groups.filter(name__in=['R&D Head', 'Marketing Head', 'Volunteer', 'Donor']).count() == 0)
@csrf_exempt
@login_required
def vol_dashboard(request):
    data = {}
    config = Config.objects.filter(id=1).values_list('fiscal_month', flat=True)[0]
    con, ml = dashboard.get_month_range(config)
    data["m_list"] = ml
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    dashboard.regular_vol(data)
    data = dashboard.top_vol(data)
    data = dashboard.vol_attendance(data, con)
    data = dashboard.vol_role(data)
    data = dashboard.no_story_teller(data)
    data = dashboard.vol_bday(data)
    data = dashboard.vol_ani(data)
    print(data)
    if request.method == "POST":
        if 'input' in request.POST:
            input = request.POST.get('input')

            pid = Profile.objects.annotate(fullname=Concat('user__first_name', Value(' '), 'user__last_name')).filter(
                user__groups__name="Volunteer", user__first_name__startswith=input)
            vol = pid.values_list('fullname', flat=True)
            json_stuff = json.dumps({'volunteer': list(vol)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            value = request.POST.get('value')
            vol = Profile.objects.filter(user__first_name=value.split()[0], user__last_name=value.split()[1],
                                         user__groups__name="Volunteer")
            data = serializers.serialize('json', list(vol))
            json_stuff = json.dumps({'fname': value, 'data': data})
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'dashboard/vol_dash.html', context=data)


@user_passes_test(lambda u: u.groups.filter(
    name__in=['President', 'R&D Head', 'Marketing Head', 'HR Head', 'Project Lead', 'Volunteer', 'Donor']).count() == 0)
@login_required
@csrf_exempt
def donor_dashboard(request):
    data = {}
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data = dashboard.monthly_donation(data)
    data = dashboard.don_nation(data)
    data = dashboard.don_country(data)
    data = dashboard.don_by_year(data)
    data = dashboard.upcoming_tasks(data)
    data = dashboard.upcoming_pledges(data)
    print(data)
    if request.method == "GET" and request.is_ajax():
        value = request.GET.get('value')
        donor = Donor.objects.filter(first_name=value.split()[0], last_name=value.split()[1])
        print(donor)
        result = dashboard.email_history(donor.values_list('email', flat=True)[0])
        print(result)
        json_stuff = json.dumps(result)
        return HttpResponse(json_stuff, content_type="application/json")
    if request.method == "POST":
        if 'input' in request.POST:
            input = request.POST.get('input')
            did = Donor.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
                first_name__startswith=input)
            donor = did.values_list('fullname', flat=True)
            json_stuff = json.dumps({'donor': list(donor)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            value = request.POST.get('value')
            year = request.POST.get('year')
            donor = Donor.objects.filter(first_name=value.split()[0], last_name=value.split()[1])
            donation = Donation.objects.filter(donated_by__in=donor)
            data = serializers.serialize('json', list(donor), fields=(
            'image', 'email', 'contact_number', 'address1', 'address2', 'city', 'state', 'country', 'zip', 'dob',
            'project__project_name', 'company', 'position', 'twitter', 'account_no', 'program_pref', 'zoom', 'skype',
            'linkedin', 'facebook', 'instagram', 'account_manager', 'next_task', 'next_task_date', 'note', 'stage',
            'nationality', 'introduced_by'))
            date = [datetime.strftime(d, "%d-%b-%y") for d in donation.values_list('date', flat=True)]
            amount = donation.values_list('amount', flat=True)
            new_data = {}
            g = Gift.objects.filter(donor__in=donor)
            gift = dict(zip(list(g.values_list("item", flat=True)), list(g.values_list("value", flat=True))))
            don = dict(zip(list(date), list(amount)))
            new_data = dashboard.monthly_donation(new_data, donor, year)
            new_data = dashboard.don_by_year(new_data, donor, year)
            new_data = dashboard.total_donation(new_data, donor)
            new_data = dashboard.assigned_donor_tasks(new_data,donor)
            json_stuff = json.dumps({'fname': value, 'data': data, 'donation': don, 'gik': gift, 'new_data': new_data},sort_keys=True, indent=1, cls=DjangoJSONEncoder)
            print(json_stuff)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'select' in request.POST:
            new_data = {}
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Year':
                d = Donation.objects.all().values_list('date__year', flat=True)
            elif sel == 'All':
                new_data = dashboard.don_by_year(new_data)
                json_stuff = json.dumps(new_data)
                return HttpResponse(json_stuff, content_type="application/json")
            json_stuff = json.dumps({'value': list(set(d))})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'v_input' in request.POST:
            input = request.POST.get('v_input')
            uid = User.objects.filter(username__startswith=input, groups__name="Volunteer")
            volunteer = uid.values_list('username', flat=True)
            json_stuff = json.dumps({'volunteer': list(volunteer)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'duedate' in request.POST:
            volunteer = request.POST.get('volunteer')
            task = request.POST.get('task')
            date = request.POST.get('duedate')
            time = request.POST.get('time')
            type = request.POST.get('type')
            frm = "%Y-%m-%d %I:%M %p"
            due_date = datetime.strptime(date + " " + time, frm)
            print(volunteer, task)
            Task.objects.create(user=Profile.objects.get(user=User.objects.get(username=volunteer)),
                                assigned_by=request.user.profile, task=task, date=due_date, type=type)
        elif 'pledge' in request.POST:
            donor = request.POST.get('donor')
            pledge = request.POST.get('pledge')
            amount = request.POST.get('amount')
            date = request.POST.get('date')
            print(donor, pledge)
            Pledge.objects.create(
                donor=Donor.objects.filter(first_name=donor.split()[0], last_name=donor.split()[1])[0], pledge=pledge,
                amount=amount, date=date)
        elif 'gift' in request.POST:
            donor = request.POST.get('donor')
            gift = request.POST.get('gift')
            value = request.POST.get('gift_value')
            date = request.POST.get('date')
            print(gift, value)
            Gift.objects.create(donor=Donor.objects.filter(first_name=donor.split()[0], last_name=donor.split()[1])[0],
                                item=gift, value=value, date=date)
        elif 'field' in request.POST:
            new_data = {}
            field = request.POST.get('field')
            val = request.POST.get('fvalue')
            donor = request.POST.get('donor')
            print(field, val, donor)
            d = ''
            if donor is not '':
                d = Donor.objects.filter(first_name=donor.split()[0], last_name=donor.split()[1])

            new_data = dashboard.monthly_donation(new_data, d, val)
            new_data = dashboard.don_by_year(new_data, d, val)
            json_stuff = json.dumps(new_data)
            print(new_data)
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'dashboard/donor_dash.html', context=data)


@user_passes_test(lambda u: u.groups.filter(name__in=['HR Head', 'Project Lead', 'Volunteer', 'Donor']).count() == 0)
@csrf_exempt
@login_required
def child_dashboard(request):
    data = {}
    config = Config.objects.filter(id=1).values_list('fiscal_month', flat=True)[0]
    con, ml = dashboard.get_month_range(config)
    data["m_list"] = ml
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data = dashboard.child_attendance(data, con)
    data = dashboard.top_kid(data)
    data = dashboard.kid_years(data, con)
    data = dashboard.kid_stats(data, con)
    data = dashboard.kid_bday(data)
    data = dashboard.mem_ani(data)
    data = dashboard.no_of_kids(data, con)

    print(data)
    if request.method == "POST":
        if 'input' in request.POST:
            input = request.POST.get('input')

            pid = Kid.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name')).filter(
                first_name__startswith=input)
            vol = pid.values_list('fullname', flat=True)
            json_stuff = json.dumps({'volunteer': list(vol)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            value = request.POST.get('value')
            if " " not in value:
                kid = Kid.objects.filter(first_name=value.split()[0], last_name=value.split()[1])
            else:
                kid = Kid.objects.filter(first_name=value.split()[0])
            print(kid)
            new_data = {}
            data = serializers.serialize('json', list(kid), fields=(
            'first_name', 'last_name', 'house_name', 'gender', 'dob', 'age', 'hobbies', 'sibling_name', 'school_name',
            'class_no', 'wish_to_pursue', 'attended_sessions', 'attending_sessions', 'date', 'image'))
            new_data = dashboard.child_attendance(new_data, con, None, None, kid.values_list('pk', flat=True)[0])
            new_data = dashboard.kid_session_history(new_data, kid.values_list('pk', flat=True)[0])
            new_data = dashboard.kid_galery(new_data, kid)
            print(new_data)
            json_stuff = json.dumps({'fname': value, 'data': data, 'new_data': new_data,
                                     'library': kid.values_list('project__project_name', flat=True)[0]})
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'dashboard/child_dash.html', context=data)


@user_passes_test(lambda u: u.groups.filter(name__in=['Volunteer']).count() == 0)
@csrf_exempt
@login_required
def proj_dashboard(request):
    data = {}
    config = Config.objects.filter(id=1).values_list('fiscal_month', flat=True)[0]
    con, ml = dashboard.get_month_range(config)
    data["m_list"] = ml
    print('view', config, ml)
    pid = Profile.objects.filter(user=request.user.profile.user)
    print(123,)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data["config"] = config
    print(data['config'])
    y_list = []
    if Project.objects.exists():
        p = Project.objects.all().order_by("date").values_list('date__year')[0][0]
        for i in range(today.year, p-1, -1):
            y_list.append(i)
    data["year"] = y_list
    if pid.values_list('project', flat=True)[0] is not None:
        c = Project.objects.filter(pk=pid.values_list('project', flat=True)[0])
    else:
        c = Project.objects.filter(country='India')
    print(c)
    data = dashboard.monthly_session(data, con, c)
    data = dashboard.child_attendance(data, con)
    data = dashboard.session_prog(data, con, c)
    data = dashboard.vol_attendance(data, con, c)
    data = dashboard.volunteer_list(data, c)
    data = dashboard.key_detail(data, c)
    data = dashboard.highlight(data, c)
    print(data)
    if request.method == "POST":
        if 'fiscalv' in request.POST:
            fv = request.POST.get('fiscalv')
            ft = request.POST.get('fiscalt')
            config = Recruitment_Form_Config.objects.filter(id=1)
            config.update(fiscal_month=fv)
        elif 'select' in request.POST:
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)
            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' or 'year' in request.POST:
            new_data = {}
            if request.user.profile.project is not None:
                year = request.POST.get('year')
                p = Profile.objects.filter(user=request.user).values_list('project', flat=True)[0]
                f = Project.objects.filter(pk=p)
                print(f)
            else:
                new_data = {}
                field = request.POST.get('field')
                val = request.POST.get('value')
                year = request.POST.get('year')
                print(field, val, Project.objects.filter(project_name=val))
                if field == 'Project':
                    f = Project.objects.filter(project_name=val)
                    print(f)
                elif field == 'Country':
                    f = Project.objects.filter(country=val)
                elif field == 'Chapter':
                    f = Project.objects.filter(state=val)
            new_data = dashboard.child_attendance(new_data, con, f, year)
            new_data = dashboard.vol_attendance(new_data, con, f, year)
            new_data = dashboard.key_detail(new_data, f)
            new_data = dashboard.session_prog(new_data, con, f, year)
            new_data = dashboard.monthly_session(new_data, con, f, year)
            new_data = dashboard.volunteer_list(new_data, f)
            new_data = dashboard.highlight(new_data, f, year)
            json_stuff = json.dumps(new_data)
            print(new_data)
            return HttpResponse(json_stuff, content_type="application/json")

    return render(request, 'dashboard/p_dash.html', context=data)


@user_passes_test(lambda u: u.groups.filter(
    name__in=['R&D Head', 'Marketing Head', 'Project Lead', 'Volunteer', 'Donor']).count() == 0)
@csrf_exempt
@login_required
def rec_dashboard(request):
    data = {}
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    y_list = []
    if Recruit.objects.exists():
        p = Recruit.objects.all().order_by("timestamp").values_list('timestamp__year')[0][0]
        for i in range(today.year, p - 1, -1):
            y_list.append(i)
    data["year"] = y_list
    data = dashboard.total_applications(data)
    data = dashboard.pending_applications(data)
    data = dashboard.in_process_applications(data)
    data = dashboard.approved_applications(data)
    data = dashboard.rec_role(data)

    if request.method == "POST":
        if 'year' in request.POST:
            new_data = {}
            year = request.POST.get('year')
            new_data = dashboard.total_applications(new_data, year)
            new_data = dashboard.pending_applications(new_data, year)
            new_data = dashboard.in_process_applications(new_data, year)
            new_data = dashboard.approved_applications(new_data, year)
            new_data = dashboard.rec_role(new_data, year)
            print(123, new_data)
            json_stuff = json.dumps(new_data)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'status' in request.POST:
            id = request.POST.get('id')
            status = request.POST.get('status')
            Recruit.objects.filter(pk=id).update(status=status)
            print(status)

    print(data)
    return render(request, 'dashboard/rec_dash.html', context=data)


@csrf_exempt
def mailchimp(request):
    data = {}
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data.update(get_campaigns())
    data.update(get_members())
    if request.method == "POST":
        if "subject" in request.POST:
            id = request.POST.get('id')
            tempid = request.POST.get('tempid')
            type = request.POST.get('type')
            recipients = request.POST.get('recipients')
            title = request.POST.get('title')
            from_name = request.POST.get('from')
            reply_to = request.POST.get('to')
            url = request.POST.get('url')
            s_title = request.POST.get('s_title')
            desc = request.POST.get('desc')
            subject = request.POST.get('subject')
            preview = request.POST.get('preview')
            content = request.POST.get('content')
            print(desc)
            edit_campaign(id, type, recipients, title, from_name, reply_to, url, s_title, desc, subject,
                          preview, tempid, content)
            print(1, id, recipients)
        else:
            id = request.POST.get('id')
            action = request.POST.get('action')
            if action == 'read' or action == 'edit':
                res, content = get_campaign(id)
                data = res
                data.update(get_lists())
                if data["type"] == "plaintext":
                    data["type"] = "Plain Text"
                elif data["type"] == "regular":
                    data["type"] = "Regular"
                data["content"] = content
                json_stuff = json.dumps(data)
                print(1)
                # print(json_stuff)
                if action == "edit" and data["type"] == "Regular":
                    data.update(get_templates())
                    json_stuff = json.dumps(data)
                    print(2, json_stuff)
                    return HttpResponse(json_stuff, content_type="application/json")
                return HttpResponse(json_stuff, content_type="application/json")

            elif action == 'delete':
                res = delete_campaign(id)
                print(res, res.text)
                if res.status_code == 200:
                    return redirect('mailchimp')
                else:
                    json_stuff = json.dumps({'notify': 'Error occurred while deleting.'})
                    return HttpResponse(json_stuff, content_type="application/json")

    print(data)
    return render(request, 'mailchimp/inbox.html', context=data)


def gallery_op(request, c):
    data = {}
    y = Project.objects.all().order_by("date").values_list('date__year')[0][0]
    data['month'] = ['ALL', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    y_list = ['ALL']
    for i in range(today.year, y - 1, -1):
        y_list.append(i)
    data["year"] = y_list
    data = gallery.gallery(data, c)
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    if request.method == "POST":
        if 'select' in request.POST:
            sel = request.POST.get('select')
            year = request.POST.get('year')
            month = request.POST.get('month')
            print(sel)
            if sel == 'All':
                pass
            elif sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)

            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            new_data = {}
            field = request.POST.get('field')
            val = request.POST.get('value')
            year = request.POST.get('year')
            month = request.POST.get('month')
            print(field)
            if field == 'Project':
                f = Project.objects.filter(project_name=val)
            elif field == 'Country':
                f = Project.objects.filter(country=val)
            elif field == 'Chapter':
                f = Project.objects.filter(state=val)
    return data


@user_passes_test(lambda u: u.groups.filter(name__in=['HR Head', 'Donor']).count() == 0)
@csrf_exempt
def session_gallery(request):
    data = gallery_op(request, Session)
    data["active"] = 1
    if request.method == "POST":
        if 'value' in request.POST:
            val = request.POST.get('value')
            field = request.POST.get('field')
            year = request.POST.get('year')
            month = request.POST.get('month')
            f = None
            if field == 'Project':
                f = Project.objects.filter(project_name=val)
            elif field == 'Country':
                f = Project.objects.filter(country=val)
            elif field == 'Chapter':
                f = Project.objects.filter(state=val)
            if year == 'ALL':
                year = None
            if month == 'ALL':
                month = None
            data = gallery.gallery(data, Session, f, year, month)
            json_stuff = json.dumps(data)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'select' in request.POST:
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)
            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'gallery.html', context=data)


@user_passes_test(lambda u: u.groups.filter(name__in=['HR Head', 'Donor']).count() == 0)
@csrf_exempt
def project_gallery(request):
    data = gallery_op(request, Project)
    data["active"] = 2
    if request.method == "POST":
        if 'value' in request.POST:
            val = request.POST.get('value')
            field = request.POST.get('field')
            year = request.POST.get('year')
            month = request.POST.get('month')
            print(val)
            if year == 'ALL':
                year = None
            if month == 'ALL':
                month = None
            data = gallery.gallery(data, Project, val, year, month)
            json_stuff = json.dumps(data)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'select' in request.POST:
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)
            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'gallery.html', context=data)


@user_passes_test(lambda u: u.groups.filter(
    name__in=['Donor', 'Volunteer', 'R&D Head', 'HR Head', 'Project Lead', 'Donor']).count() == 0)
@csrf_exempt
def donor_gallery(request):
    data = gallery_op(request, Donor)
    data["active"] = 3
    if request.method == "POST":
        if 'value' in request.POST:
            val = request.POST.get('value')
            field = request.POST.get('field')
            year = request.POST.get('year')
            month = request.POST.get('month')
            f = None
            if field == 'Project':
                f = Project.objects.filter(project_name=val)
            elif field == 'Country':
                f = Project.objects.filter(country=val)
            elif field == 'Chapter':
                f = Project.objects.filter(state=val)
            if year == 'ALL':
                year = None
            if month == 'ALL':
                month = None
            data = gallery.gallery(data, Donor, f, year, month)
            json_stuff = json.dumps(data)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'select' in request.POST:
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)
            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'gallery.html', context=data)


@user_passes_test(lambda u: u.groups.filter(name__in=['Donor']).count() == 0)
@csrf_exempt
def kid_gallery(request):
    data = gallery_op(request, Kid)
    data["active"] = 4
    if request.method == "POST":
        if 'value' in request.POST:
            val = request.POST.get('value')
            field = request.POST.get('field')
            year = request.POST.get('year')
            month = request.POST.get('month')
            f = None
            if field == 'Project':
                f = Project.objects.filter(project_name=val)
            elif field == 'Country':
                f = Project.objects.filter(country=val)
            elif field == 'Chapter':
                f = Project.objects.filter(state=val)
            if year == 'ALL':
                year = None
            if month == 'ALL':
                month = None
            data = gallery.gallery(data, Kid, f, year, month)
            json_stuff = json.dumps(data)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'select' in request.POST:
            sel = request.POST.get('select')
            print(sel)
            if sel == 'Project':
                p = Project.objects.all().values_list('project_name', flat=True)
            elif sel == 'Country':
                p = Project.objects.all().values_list('country', flat=True)
            elif sel == 'Chapter':
                p = Project.objects.all().values_list('state', flat=True)
            json_stuff = json.dumps({'value': list(set(p))})
            return HttpResponse(json_stuff, content_type="application/json")
    return render(request, 'gallery.html', context=data)


def signin(request):
    if request.method == "POST":
        form = LogInForm(data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            group = request.user.groups.values_list('name', flat=True).first()
            if user is not None:
                # request.session["username"] = user.id
                # request.session.set_expiry(10)
                auth_login(request, user)
                return redirect('profile')
            elif user_obj.is_active is False:
                messages.error(request, "* Verify your Email ID using the verification link sent.")
                messages.error(request, "* Your account might be disabled")
            else:
                messages.error(request, '* Invalid credentials.')
        except:
            messages.error(request, '* User does not exist. Please talk to the Admin.')
    else:
        form = LogInForm()
    return render(request, 'profile/index.html', {'form': form, 'action': 'signin'})


def signout(request):
    auth_logout(request)
    return redirect("signin")


def login_cancelled(request):
    return redirect(request, 'signin')


@login_required
@csrf_exempt
def profile(request):
    data = {}
    pid = Profile.objects.filter(user=request.user.profile.user)
    profile = json.dumps(list(pid.values()), indent=4, cls=DjangoJSONEncoder)
    attendance = Attendance.objects.filter(user=request.user.profile, attendance_approved=True)
    sessions = Session.objects.filter(project=request.user.profile.project)
    att = (len(attendance) / len(sessions)) * 100 if len(sessions) != 0 else 0
    data['att'] = [len(attendance), len(sessions) - len(attendance)]
    data['att_p'] = att
    data['roles'] = list(Role.objects.all().values_list('role',flat=True))
    print(data['roles'])
    c = 3
    for k, v in json.loads(profile)[0].items():
        if k not in ["signup_confirmation", "id", "user_id", "image"]:
            if v in [None, '']:
                data[k] = ""
            else:
                if k == "address":
                    data['addr1'] = v.split("; ")[0]
                    data['addr2'] = v.split("; ")[1]
                else:
                    data[k] = v
            if v not in [None, '', "[]", "0", "+91-", []]:
                c += 1
    percent = int((c / 19) * 100)
    data['strength'] = percent
    data['first_name'] = request.user.first_name
    data['last_name'] = request.user.last_name
    data['email'] = request.user.email
    data['project'] = request.user.profile.project.project_name if request.user.profile.project is not None else ''
    av = pid.values_list("image", flat=True)[0]
    data["image"] = settings.MEDIA_URL + av
    data["zoom"] = request.user.profile.zoom
    data["skype"] = request.user.profile.skype
    data["linkedin"] = request.user.profile.linkedin
    data["facebook"] = request.user.profile.facebook
    data["instagram"] = request.user.profile.instagram
    task_list = Task.objects.filter(user=request.user.profile, status="Pending").order_by('date')
    data['tasks'] = task_list
    print(task_list)
    if request.method == "POST":
        if 'imgbase64' in request.POST:
            imgdata = request.POST.get('imgbase64')
            print(imgdata)
            import base64
            from PIL import Image
            from io import BytesIO
            imgdata = imgdata.replace("data:image/png;base64,", "") + "=="
            print(len(imgdata))
            im = Image.open(BytesIO(base64.b64decode(imgdata)))
            url = "avatar/" + request.user.username + ".png"
            im.save(os.path.join(settings.MEDIA_ROOT,url), 'PNG')
            pid = Profile.objects.filter(user=request.user)
            #print(request.user.profile.user, request.user, os.path.join(settings.MEDIA_ROOT,url), url)
            pid.update(image=url)

        elif 'input' in request.POST:
            input = request.POST.get('input')
            uid = User.objects.filter(username__startswith=input, groups__name="Volunteer")
            volunteer = uid.values_list('username', flat=True)
            json_stuff = json.dumps({'volunteer': list(volunteer)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            value = request.POST.get('value')
            uid = User.objects.get(username=value)
            aid = Attendance.objects.filter(user=uid.id, attendance_submitted=True, attendance_approved=False)
            sid = Session.objects.filter(id__in=aid.values_list('session', flat=True))
            session = sid.values_list('library_name', flat=True)
            location = sid.values_list('location', flat=True)
            id = sid.values_list('id', flat=True)
            json_stuff = json.dumps({'id': list(id), 'attendance': list(session), 'location': list(location)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'duedate' in request.POST:
            volunteer = request.POST.get('volunteer')
            task = request.POST.get('task')
            date = request.POST.get('duedate')
            time = request.POST.get('time')
            type = request.POST.get('type')
            frm = "%Y-%m-%d %I:%M %p"
            due_date = datetime.strptime(date + " " + time, frm)
            print(volunteer, task)
            Task.objects.create(user=Profile.objects.get(user=User.objects.get(username=volunteer)),
                                assigned_by=request.user.profile, task=task, date=due_date, type=type)
        elif 'alltask' in request.POST or 'todo' in request.POST:
            if 'alltask' in request.POST:
                tasks = Task.objects.select_related('user').filter(assigned_by=request.user.profile).order_by('date')
                date = [dt.date() for dt in tasks.values_list('date', flat=True)]
                task = tasks.values_list('task', flat=True)
                assigned_to = tasks.values_list('user__user__username', flat=True)
                status = tasks.values_list('status', flat=True)
                json_stuff = json.dumps(
                    {'date': list(date), 'task': list(task), 'assigned_to': list(assigned_to), 'status': list(status)},
                    sort_keys=True, indent=1, cls=DjangoJSONEncoder)
                return HttpResponse(json_stuff, content_type="application/json")
            elif 'todo' in request.POST:
                tasks = Task.objects.filter(user=request.user.profile).exclude(status="Pending").order_by(
                    'date').annotate(
                    fullname=Concat('assigned_by__user__first_name', Value(' '), 'assigned_by__user__last_name'))
                date = [dt.date() for dt in tasks.values_list('date', flat=True)]
                task = tasks.values_list('task', flat=True)
                assigned_by = tasks.values_list('fullname', flat=True)
                status = tasks.values_list('status', flat=True)

                json_stuff = json.dumps(
                    {'date': list(date), 'task': list(task), 'assigned_by': list(assigned_by), 'status': list(status)},
                    sort_keys=True, indent=1, cls=DjangoJSONEncoder)
                print(json_stuff)
                return HttpResponse(json_stuff, content_type="application/json")
                # print(tasks)
        elif 'checkbox' in request.POST:
            checkbox = request.POST.getlist('checkbox')
            tasks = Task.objects.filter(id__in=checkbox)
            tasks.update(status="Done")
        elif 'nick-name' in request.POST:

            nick_name = request.POST.get('nick-name')
            dob = request.POST.get('dob') or None
            c_name = request.POST.get('c-name')
            pos = request.POST.get('pos')
            interest = request.POST.get('interest')
            chapter = request.POST.get('chapter')
            project = request.POST.get('project')
            fplan = request.POST.get('fplan')
            role = request.POST.get('role')
            pid.update(nick_name=nick_name, dob=dob, company=c_name, position=pos, role=role_dict[role],
                       hobbies=interest,
                       chapter=chapter, future_plans=fplan)
        elif 'addr1' in request.POST:
            zoom = request.POST.get('zoom')
            skype = request.POST.get('skype')
            linkedin = request.POST.get('linkedin')
            facebook = request.POST.get('facebook')
            instagram = request.POST.get('instagram')
            twitter = request.POST.get('twitter')
            addr1 = request.POST.get('addr1')
            addr2 = request.POST.get('addr2')
            city = request.POST.get('city')
            state = request.POST.get('state')
            country = request.POST.get('country')
            phone = request.POST.get('phone')
            if addr1 is not None and addr2 is not None:
                address = str(addr1) + "; " + str(addr2)
            else:
                address = ""
            pid.update(address=address, city=city, state=state, country=country, contact_number=phone,
                       zoom=zoom, skype=skype, linkedin=linkedin, facebook=facebook,twitter=twitter,
                       instagram=instagram)
        return redirect('profile')
    return render(request, 'profile/profile.html', context=data)


@user_passes_test(lambda u: u.groups.filter(name__in=['Donor']).count() == 0)
@login_required
@csrf_exempt
def calender(request):
    data = {}
    session_kv = {}
    k = "https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id=86jm210h5i5hd7&scope=r_fullprofile r_emailaddress rw_company_adminw_share&state=8897239179ramya&redirect_uri=http://127.0.0.1:8000/accounts/profile"
    k = requests.get(k)
    print(k.text)
    data['sessions'] = Session.objects.all()
    pid = Profile.objects.filter(user=request.user.profile.user)
    av = pid.values_list("image", flat=True)[0]
    if av == "":
        name = request.user.get_full_name()
        data["image"] = avinit.get_image_data_url(name)
    else:
        data["image"] = settings.MEDIA_URL + av
    if request.method == "POST":
        if 'date' in request.POST:
            date = request.POST.get('date')
            if date:
                sid = Session.objects.filter(date__startswith=date)
                data = {}
                if sid:
                    data['warning'] = ""
                    objs = serializers.serialize('json', sid, fields=['library_name', 'location'])
                    for obj in json.loads(objs):
                        print(obj)
                        session_kv.update(
                            {str(obj['pk']): obj['fields']['library_name'] + " - " + obj['fields']['location']})

                    data['session_select'] = json.dumps(session_kv)
                else:
                    data['session_select'] = ""
                    data['warning'] = "Selected date had no sessions. Kindly change the date."
                print(session_kv)
                return JsonResponse(data)
        elif 'session' in request.POST:
            date = request.POST.get('session_date')
            session = request.POST.get('session')
            print(session)
            sid = Session.objects.filter(date__startswith=date)
            objs = serializers.serialize('json', sid, fields=['library_name', 'location'])
            for obj in json.loads(objs):
                session_kv.update({str(obj['pk']): obj['fields']['library_name'] + " - " + obj['fields']['location']})
            sid = Session.objects.get(date__startswith=date, library_name=session_kv[session].split(" - ")[0])
            try:
                if Attendance.objects.get(user=request.user.profile, session=sid, attendance_submitted=True):
                    json_stuff = json.dumps({'notification': "Attendance already registered!"})
                    return HttpResponse(json_stuff, content_type="application/json")
            except ObjectDoesNotExist:
                Attendance.objects.create(user=request.user.profile, session=sid, attendance_submitted=True)
                json_stuff = json.dumps({'notification': "Attendance Updated! Waiting for approval."})
                return HttpResponse(json_stuff, content_type="application/json")

        elif 'input' in request.POST:
            input = request.POST.get('input')
            print(input)
            uid = User.objects.filter(username__startswith=input, groups__name="Volunteer")
            volunteer = uid.values_list('username', flat=True)
            json_stuff = json.dumps({'volunteer': list(volunteer)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'value' in request.POST:
            value = request.POST.get('value')
            print(value)
            uid = User.objects.get(username=value)
            aid = Attendance.objects.filter(user=uid.id, attendance_submitted=True, attendance_approved=False)
            print(aid.values_list('session', flat=True))
            sid = Session.objects.filter(id__in=aid.values_list('session', flat=True))
            session = sid.values_list('library_name', flat=True)
            location = sid.values_list('location', flat=True)
            id = sid.values_list('id', flat=True)
            print(session)
            json_stuff = json.dumps({'id': list(id), 'attendance': list(session), 'location': list(location)})
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'selected' in request.POST:
            selected = request.POST.get('selected')
            p = Session.objects.filter(pk=selected).values_list('project')
            ka = Kid_Attendance.objects.filter(session=selected).values_list('kid', flat=True)
            k = Kid.objects.filter(library=list(p)[0]).exclude(pk__in=ka).annotate(
                fullname=Concat('first_name', Value(' '), 'last_name'))
            print(k)
            id = k.values_list('pk', flat=True)
            name = k.values_list('fullname', flat=True)
            json_stuff = json.dumps(dict(zip(list(id), list(name))))
            print(json_stuff)
            return HttpResponse(json_stuff, content_type="application/json")
        elif 'cat_approval' in request.POST:
            date = request.POST.get('session_date')
            session = request.POST.get('session2')
            approval = request.POST.getlist('cat_approval')
            for a in approval:
                Kid_Attendance.objects.create(kid=Kid.objects.get(pk=int(a)), session=Session.objects.get(pk=session),
                                              attendance=True)
            print(date, session, approval)
        elif 'volunteer' in request.POST:
            volunteer = request.POST.get('volunteer')
            approval = request.POST.getlist('approval')
            print(volunteer, approval)
            aid = Attendance.objects.filter(user=Profile.objects.get(user=User.objects.get(username=volunteer)),
                                            session__in=approval)
            aid.update(attendance_approved=True)
    return render(request, 'profile/calender.html', context=data)
