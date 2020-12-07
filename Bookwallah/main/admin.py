from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseAdmin,GroupAdmin as GAdmin
from import_export import resources
from import_export.fields import Field
from django.contrib import admin
from django.contrib.auth.models import User,Group
from .models import *
from django.contrib.auth.hashers import make_password
# Register your models here.

#admin.site.register(Session)
#admin.site.register(Project)
#admin.site.register(Kid)
#admin.site.register(Donation)
#admin.site.register(Donor)
#admin.site.register(Expense)
class UserResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        value = row['password']
        row['password'] = make_password(value)

    class Meta:
        model = User
        exclude = ('last_login','date_joined','user_permissions')

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

@admin.register(Config)
class Config(ImportExportModelAdmin):
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
@admin.register(Issues)
class Issues(ImportExportModelAdmin):
    pass
@admin.register(Volunteer_Testimonial)
class Volunteer_Testimonial(ImportExportModelAdmin):
    pass
@admin.register(Donor_Testimonial)
class Donor_Testimonial(ImportExportModelAdmin):
    pass
#@admin.register(Role)
#class Role(ImportExportModelAdmin):
#    pass


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

@admin.register(Kid)
class Kid(ImportExportModelAdmin):
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
