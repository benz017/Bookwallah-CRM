from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class LogInForm(AuthenticationForm):
    username = forms.CharField(max_length=150, help_text='Username', widget=forms.TextInput(attrs={'class': "form-control", 'id':"username",'placeholder':"Username",'style':"margin-top:7px;margin-left:0px;" }))
    password = forms.CharField(max_length=16,  validators=[MinLengthValidator(6)], help_text='Password', widget=forms.PasswordInput(attrs={'class': "form-control", 'id':"password" ,'placeholder':"Password",'style':"margin-top:7px;margin-left:0px;" }))

    class Meta:
        model = User
        fields = ('username', 'password')
