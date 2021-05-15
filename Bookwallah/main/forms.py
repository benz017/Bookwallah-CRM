from django import forms
from django.forms import Form
from django.forms import DateField, CharField, ChoiceField, TextInput
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class LogInForm(AuthenticationForm):
    username = forms.CharField(max_length=150, help_text='Username', widget=forms.TextInput(attrs={'class': "form-control", 'id':"username",'placeholder':"Username",'style':"margin-top:7px;margin-left:0px;" }))
    password = forms.CharField(max_length=16,  validators=[MinLengthValidator(8)], help_text='Password', widget=forms.PasswordInput(attrs={'class': "form-control", 'id':"password" ,'placeholder':"Password",'style':"margin-top:7px;margin-left:0px;" }))

    class Meta:
        model = User
        fields = ('username', 'password')


class PasswordChangeCustomForm(PasswordChangeForm):
    error_css_class = 'has-error'
    error_messages = {'password_incorrect':
                          "Password Incorrect. Please check."}
    old_password = forms.CharField(required=True, label='Current Password',
                             widget=forms.PasswordInput(attrs={
                                 'class': 'form-control-2'}),
                             error_messages={
                                 'required': 'Please enter your current password.'})

    new_password1 = forms.CharField(required=True, label='New Password',
                              widget=forms.PasswordInput(attrs={
                                  'class': 'form-control-2'}),validators=[MinLengthValidator(8)],
                              error_messages={
                                  'required': 'Please enter the new password.'})
    new_password2 = forms.CharField(required=True, label='Re-enter Password',
                              widget=forms.PasswordInput(attrs={
                                  'class': 'form-control-2'}),validators=[MinLengthValidator(8)],
                              error_messages={
                                  'required': 'Please re-enter the new password.'})


class SearchForm(forms.ModelForm):
    first_name = CharField(required=False)
    date = DateField(required=False, widget=TextInput(
        attrs={
            'filter_method': '__gte',
        }
    ))

class YourFormSearch(Form):
    gen = (('Male', 'Male'), ('Female', 'Female'))
    first_name = CharField(required=False)
    last_name = CharField(required=False)
    gender = ChoiceField(required=False,choices=gen)