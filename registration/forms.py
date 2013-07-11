from django import forms
from django.db import transaction
from events.event import EventHandler
from django.db import models
from django.forms import ModelForm
from registration import models
from django.contrib.auth.models import User
from registration.models import UserProfile
from core.models import Device


class UserForm (ModelForm):
    password = forms.CharField(widget=forms.PasswordInput) 
    # in order to do <input type="password"/> 
    class Meta:
        model = User
        include = ('username', 'password')


class UserProfileForm (ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user')


class DeviceForm (ModelForm):
    class Meta:
        model = Device
        exclude = ('is_reserved', 'interfaces', 'admin', 'owner')
