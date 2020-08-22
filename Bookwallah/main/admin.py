from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.contrib.auth.models import User
from .models import *
# Register your models here.
#admin.site.register(Profile)
#admin.site.register(Session)
#admin.site.register(Project)
#admin.site.register(Kid)
#admin.site.register(Donation)
#admin.site.register(Donor)
#admin.site.register(Expense)
admin.site.register(Config)
admin.site.register(Recruit)
admin.site.register(Task)

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