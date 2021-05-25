from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseAdmin,GroupAdmin as GAdmin
from import_export import resources
from .util.mail import email_users as eu
from import_export.fields import Field
from django.contrib import admin
from django.contrib.auth.models import User,Group
from .models import *
from django.contrib.auth.hashers import make_password
# Register your models here.
from .tasks import email_users
from django_admin_search.admin import AdvancedSearchAdmin
from .forms import YourFormSearch,SearchForm
from django.conf.locale.es import formats as es_formats

es_formats.DATETIME_FORMAT = "d M Y H:i:s"



class UserResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        from django.apps import apps
        config = apps.get_model('main', 'EmailConfig')
        ec = config.objects.all()
        passwd = ec.values_list('user_default_password', flat=True)[0]
        row['password'] = make_password(passwd)
        ids = list(Group.objects.all().values_list('id', flat=True))
        name = list(Group.objects.all().values_list('name', flat=True))
        name = [x.lower() for x in name]
        grp = row['groups']
        row['groups'] = ids[name.index(grp.lower())]

    class Meta:
        model = User
        exclude = ('password','last_login','date_joined','user_permissions')

    def after_save_instance(self, instance: User, using_transactions: bool, dry_run: bool,):
        from django.apps import apps
        config = apps.get_model('main', 'EmailConfig')
        if dry_run is False:

            print('Task starting!!')
            ec = config.objects.all()
            passwd = ec.values_list('user_default_password', flat=True)[0]
            subject = ec.values_list('welcome_email_subject', flat=True)[0]
            msg = ec.values_list('welcome_email_message', flat=True)[0]
            try:
                email_users.delay(instance.username, instance.email, passwd,subject,msg)
            except:
                eu(instance.username, instance.email, passwd,subject,msg)

class UserAdmin(BaseAdmin, ImportExportModelAdmin):
    resource_class = UserResource

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class GroupResource(resources.ModelResource):
    class Meta:
        model = Group

class GroupAdmin(GAdmin, ImportExportModelAdmin):
    resource_class = GroupResource

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

@admin.register(EmailConfig)
class EmailConfig(ImportExportModelAdmin):
    pass
@admin.register(AppConfig)
class AppConfig(ImportExportModelAdmin):
    pass

@admin.register(Recruitment_Form_Config)
class Recruitment_Form_Config(ImportExportModelAdmin):
    pass

@admin.register(Recruit)
class Recruit(ImportExportModelAdmin):
    pass

@admin.register(Task)
class Task(ImportExportModelAdmin):
    pass

@admin.register(Pledge)
class Pledge(ImportExportModelAdmin):
    pass

@admin.register(Gift)
class Gift(ImportExportModelAdmin):
    pass

@admin.register(Kid_Attendance)
class Kid_Attendance(ImportExportModelAdmin):
    pass

@admin.register(Kid_Picture)
class Kid_Picture(ImportExportModelAdmin):
    pass
@admin.register(Session_Picture)
class Session_Picture(ImportExportModelAdmin):
    pass
@admin.register(Highlight)
class Highlight(ImportExportModelAdmin):
    pass
@admin.register(Issue)
class Issue(ImportExportModelAdmin):
    pass
@admin.register(Testimonial)
class Testimonial(ImportExportModelAdmin):
    pass

@admin.register(Role)
class Role(ImportExportModelAdmin):
    pass


@admin.register(NPSScore)
class NPSScore(ImportExportModelAdmin):
    pass

@admin.register(ChildPsychologyScore)
class ChildPsychologyScore(ImportExportModelAdmin):
    pass

@admin.register(ProSocialBehaviorScore)
class ProSocialBehaviorScore(ImportExportModelAdmin):
    pass
@admin.register(Session)
class Session(ImportExportModelAdmin):
    pass

@admin.register(Project)
class Project(ImportExportModelAdmin):
    pass
@admin.register(Profile)
class Profile(ImportExportModelAdmin):
    pass

from import_export.admin import ImportExportMixin

@admin.register(Kid)
class KidAdmin(AdvancedSearchAdmin):
    search_form = YourFormSearch


@admin.register(Kid_Import_Export)
class KidImportExport(ImportExportModelAdmin):
    pass

@admin.register(Donation)
class Donation(ImportExportModelAdmin):
    pass

@admin.register(Donor)
class Donor(ImportExportModelAdmin):
    pass

@admin.register(Expense)
class Expense(ImportExportModelAdmin):
    pass

@admin.register(Attendance)
class Attendance(ImportExportModelAdmin):
    pass
