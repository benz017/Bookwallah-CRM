from import_export import resources
from django.contrib.auth.models import User
from .models import Profile, Session, Attendance, Task, Project,Donor,Donation


class UserResource(resources.ModelResource):
    class Meta:
        model = User