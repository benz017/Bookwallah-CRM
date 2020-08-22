from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

from django_mysql.models import ListCharField
from django.forms import MultiValueField
import avinit
import json
months = ((1,'JAN'),(2,'FEB'),(3,'MAR'),(4,'APR'),(5,'MAY'),(6,'JUN'),(7,'JUL'),(8,'AUG'),(9,'SEP'),(10,'OCT'),(11,'NOV'),(12,'DEC'))


class Config(models.Model):
    fiscal_month = models.IntegerField(choices=months,default=1)
    sheet_name = models.CharField(max_length=200,blank=True,null=True)
    username_field = models.CharField(max_length=200,blank=True,null=True)
    email_field = models.CharField(max_length=200, blank=True, null=True)
    name_field = models.CharField(max_length=300, blank=True, null=True)
    address_field = models.CharField(max_length=300, blank=True, null=True)
    contact_field = models.CharField(max_length=300, blank=True, null=True)
    tenure_field = models.CharField(max_length=300, blank=True, null=True)
    role_field = models.CharField(max_length=300, blank=True, null=True)
    prior_experience_field = models.CharField(max_length=300, blank=True, null=True)
    library_field = models.CharField(max_length=300, blank=True, null=True)
    secret_file = models.FileField(upload_to='documents',blank=True, null=True)

    def __str__(self):
        return "{} {}".format(months[int(self.fiscal_month)-1][1],self.sheet_name)


class Project(models.Model):
    project_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='project', blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.IntegerField(blank=True, null=True)
    highlights = models.CharField(max_length=3000,blank=True, null=True,default='')
    issues = models.CharField(max_length=3000, blank=True, null=True, default='')
    contact_person = models.CharField(max_length=15, blank=True, null=True, default='')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    total_kids = models.IntegerField(blank=True, null=True)
    project_lead = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name="project_lead")
    kids_bookwallah = models.IntegerField(blank=True, null=True)
    sessions_per_year = models.IntegerField(blank=True, null=True)
    project_report = models.FileField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.project_name, self.project_lead)


class Session(models.Model):
    library_name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)
    kids_attended = models.IntegerField( blank=True, null=True)
    book_name = models.CharField(max_length=100, blank=True, null=True)
    story_value = models.CharField(max_length=100, blank=True, null=True)
    activity_name = models.CharField(max_length=100, blank=True, null=True)
    activity_desc = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="session_project")
    volunteers_attended = models.CharField(max_length=100, blank=True, null=True)
    cancellation_reason = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='session',blank=True, null=True)

    def __str__(self):
        return "{} - {} - {}".format(self.library_name, self.project,self.date)


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatar', null=True, blank=True)
    nick_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True,blank=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    hobbies = models.CharField(max_length=100, blank=True, null=True)
    future_plans = models.CharField(max_length=100, blank=True, null=True)
    chapter = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="project")
    role = models.CharField(max_length=100, blank=True, null=True)
    social_media = models.CharField(max_length=100, blank=True, null=True)
    leaving_date = models.DateField(null=True, blank=True)
    document = models.FileField(blank=True,null=True)
    is_online = models.BooleanField(null=True,default=False,blank=True)
    chat_room = models.ForeignKey('chat.Room', on_delete=models.DO_NOTHING, null=True, blank=True, related_name="chat_room")

    def __str__(self):
        return "{} {}".format(self.user,self.project)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.profile.image == "":
        name = instance.get_full_name()
        av = avinit.get_avatar_data_url(name)
        import base64
        imgdata = av.replace("data:image/svg+xml;base64,", "") + "=="
        imgdata = base64.b64decode(imgdata)
        url = "\\avatar\\" + instance.username + ".svg"
        filename = settings.MEDIAFILES_DIRS[0] + url
        with open(filename, 'wb') as f:
            f.write(imgdata)
        instance.profile.avatar = url
    instance.profile.save()


class Attendance(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    attendance_submitted = models.BooleanField(default=False)
    attendance_approved = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.user,self.session)




class Donor(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    house_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True)
    image = models.ImageField(upload_to='donor', null=True, blank=True)
    nick_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="donor_project")
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=100, blank=True, null=True)
    account_no = models.CharField(max_length=100, blank=True, null=True)
    next_task = models.CharField(max_length=400, blank=True, null=True)
    next_task_date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=400, blank=True, null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)
    program_pref = models.CharField(max_length=200, blank=True, null=True)
    program_assignment = models.CharField(max_length=200, blank=True, null=True)
    account_manager = models.CharField(max_length=200, blank=True, null=True)
    gift_desc = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=200, blank=True, null=True)
    introduced_by = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, verbose_name=u"Date of Involvement")
    documents = models.FileField(null=True,blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Pledge(models.Model):
    donor = models.ForeignKey(Donor, default=2, on_delete=models.DO_NOTHING, related_name="pledge_donor")
    pledge = models.CharField(max_length=400, blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)


class Gift(models.Model):
    donor = models.ForeignKey(Donor, default=2, on_delete=models.DO_NOTHING, related_name="gift_donor")
    item = models.CharField(max_length=300, blank=True, null=True)
    value = models.CharField(max_length=32, blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)


class Task(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="assigned_to")
    task = models.CharField(max_length=400, blank=True, null=True)
    assigned_by = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, blank=True, related_name="assigned_by")
    assigned_for = models.ForeignKey(Donor, default=2, on_delete=models.DO_NOTHING, related_name="assigned_for")
    type = models.CharField(max_length=20, default="Project", blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, blank=True, null=True, default="Pending")

    def __str__(self):
        return "{} - {}".format(self.task, self.date)


class Donation(models.Model):
    donated_by = models.ForeignKey(Donor,on_delete=models.DO_NOTHING, null=True, related_name="donor")
    date = models.DateField(null=True, blank=True)
    amount = models.IntegerField(blank=True, null=True)
    pledge_amt = models.CharField(max_length=100, blank=True, null=True)
    pledge_date = models.DateField(null=True, blank=True)
    donation_channel = models.CharField(max_length=100, blank=True, null=True)
    why = models.CharField(max_length=100, blank=True, null=True)
    total_amt = models.CharField(max_length=100, blank=True, null=True)
    donation_pref = models.CharField(max_length=100, blank=True, null=True)
    acc_name = models.CharField(max_length=100, blank=True, null=True)
    gift_date = models.DateField(null=True, blank=True)
    gift_amt = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(self.donated_by, self.amount, self.date)


class Kid(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    house_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    age = models.CharField(max_length=100, blank=True, null=True)
    hobbies = models.CharField(max_length=100, blank=True, null=True)
    library = models.ForeignKey(Project, on_delete=models.DO_NOTHING, null=True)
    sibling_name = models.CharField(max_length=100, blank=True, null=True)
    class_no = models.IntegerField(blank=True, null=True)
    school_name = models.CharField(max_length=100, blank=True, null=True)
    wish_to_pursue = models.CharField(max_length=100, blank=True, null=True)
    attended_sessions = models.CharField(max_length=100, blank=True, null=True)
    attending_sessions = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now, verbose_name=u"Joining Date")
    image = models.ImageField(upload_to='kid',blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(self.library, self.first_name,self.last_name)


class Kid_Attendance(models.Model):
    kid = models.ForeignKey(Kid, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    attendance = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.kid,self.session)


class Recruit(models.Model):
    status_choices = (('Pending', 'Pending'), ('In-Process', 'In-Process'),('Approved', 'Approved'))
    timestamp = models.DateTimeField( blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=100, null=True, blank=True)
    tenure = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    prior_exp = models.CharField(max_length=1000, null=True, blank=True)
    library = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending',null=True, blank=True,choices=status_choices)

    def __str__(self):
        return "{} | {} - {}".format(self.timestamp,self.username,self.role)


class Expense(models.Model):
    currency = (('USD','USD'),('INR','INR'))
    type = (('Project Supplies','Project Supplies'), ('Supplies','Supplies'), ('Training','Training'),('Session','Session'),('Bonding','Bonding'),('Staff','Staff'),('Transport','Transport'),('Volunteers','Volunteers'),('Staff','Staff'),('Meals','Meals'),('Volunteer','Volunteer'),('Meals','Meals'),('Telephone','Telephone'),('Rewards','Rewards'),('Others','Others'))
    name_of_person = models.ForeignKey(Profile,on_delete=models.DO_NOTHING, null=True, related_name="user_name")
    date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=400, blank=True, null=True)
    expense_type = models.CharField(max_length=100, blank=True, null=True,choices=type)
    project = models.ForeignKey(Project,on_delete=models.DO_NOTHING, null=True, related_name="expense_project_name")
    receipt = models.FileField(blank=True, null=True)
    currency = models.CharField(max_length=10, choices=currency)
    credit_amount = models.IntegerField(blank=True, null=True)
    reimbursement_amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(self.name_of_person, self.reimbursement_amount, self.date)


class NPSScore(models.Model):
    state = list(set(list(Project.objects.all().values_list('state',flat=True))))
    state = ((i,i) for i in state)
    q = ['Q1','Q2','Q3','Q4']
    q = ((i,i) for i in q)
    chapter = models.CharField(max_length=30, verbose_name="Chapter", blank=True, null=True,choices=state)
    quarter = models.CharField(max_length=10, verbose_name="Quarter", blank=True, null=True,choices=q)
    year = models.CharField(max_length=10, verbose_name="Year", blank=True, null=True)
    score = models.IntegerField(verbose_name="Score (%)", blank=True, null=True)

    def __str__(self):
        return "{} ({} {})".format(self.chapter, self.quarter, self.year, )


class ChildPsychologyScore(models.Model):
    q = ['Q1', 'Q2', 'Q3', 'Q4']
    q = ((i, i) for i in q)
    project = models.ForeignKey(Project,on_delete=models.DO_NOTHING, verbose_name="Project", null=True, related_name="child_survey_project_name")
    quarter = models.CharField(max_length=10, verbose_name="Quarter", blank=True, null=True, choices=q)
    year = models.CharField(max_length=10, verbose_name="Year", blank=True, null=True)
    empathy = models.IntegerField( verbose_name="Empathy Score (%)", blank=True, null=True)
    hope = models.IntegerField(verbose_name="Hope Score (%)", blank=True,
                               null=True)
    perseverance = models.IntegerField(verbose_name="Perseverance Score (%)", blank=True,
                               null=True)
    pro_social_conduct = models.IntegerField( verbose_name="Pro Social Conduct Score (%)", blank=True,
                               null=True)

    def __str__(self):
        return "{} ({} {})".format(self.project, self.quarter, self.year)


class ProSocialBehaviorScore(models.Model):
    q = ['Q1', 'Q2', 'Q3', 'Q4']
    q = ((i, i) for i in q)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, verbose_name="Project",
                                null=True, related_name="social_behavior_project_name")
    quarter = models.CharField(max_length=10, verbose_name="Quarter", blank=True, null=True,
                               choices=q)
    year = models.CharField(max_length=10, verbose_name="Year", blank=True, null=True)
    control = models.FloatField(verbose_name="Control (New Children to Bookwallah)", blank=True,
                               null=True)
    treatment = models.FloatField(verbose_name="Treatment (Children with Bookwallah)", blank=True,
                               null=True)

    def __str__(self):
        return "{} ({} {})".format(self.project, self.quarter, self.year)


