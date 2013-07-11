# Create your views here.
from django.contrib.auth.models import User
from core.models import Device
from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponseRedirect
from django.shortcuts import  render_to_response
from django.template import RequestContext
from registration import forms
import datetime
from django.core.urlresolvers import reverse

from events.event import EventHandler
eventHandler = EventHandler()

import logging
logger = logging.getLogger(__name__)


# Registration UI (Vittorio)
def input_basic_user_details(request):

    if request.method == 'POST':
        formdata = request.POST.copy()
        try:
            User.objects.get(username=formdata['username'])
            user_form = forms.UserForm()
            user_profile_form = forms.UserProfileForm()
            mac_address = formdata['mac_address']
            in_use = True

            return render_to_response('registration_user_simple.html', 
                                      {'user_form': user_form, 'user_profile_form': user_profile_form,
                                       'mac_address': mac_address, 'in_use': in_use},
                                      context_instance=RequestContext(request))
        except User.DoesNotExist:
            formdata['date_joined'] = datetime.date.today()
            # Django doc says should be done automatically,
            # instead if not manually assigned throws error
            formdata['last_login'] = datetime.datetime.now()

            user_form = forms.UserForm(formdata)
            user_profile_form = forms.UserProfileForm(request.POST)
            if user_form.is_valid():  # saving to User object
                new_user = user_form.save()
                password = user_form.cleaned_data['password']
                new_user.set_password(password)
                new_user.is_active = True
                new_user.save()
                #if only new_user = user_form.save(), doesn't hash
                #the pwd and gives prob during login
                if user_profile_form.is_valid():
                    # saving to UserProfile object
                    new_user_profile = new_user.get_profile()
                    new_user_profile.nickname = user_profile_form.cleaned_data['nickname']
                    new_user_profile.save()

                    if 'mac_address' in formdata.keys():
                        return HttpResponseRedirect( reverse( 'registration.views.input_device_details', kwargs={'username': new_user.username}) +
                                                      '?mac_address=' + formdata['mac_address'])
                        # mac_address sent through query string
                    else:
                        return render_to_response('main.html')
                else:
                    user_form = forms.UserForm()
                    user_profile_form = forms.UserProfileForm()
                    mac_address = request.POST.get('mac_address')
                    return render_to_response(
                            'registration_user_simple.html', 
                            { 'user_form': user_form, 
                              'user_profile_form': user_profile_form,
                              'mac_address': mac_address, },
                            context_instance=RequestContext(request))
            else:
                user_form = forms.UserForm()
                user_profile_form = forms.UserProfileForm()
                mac_address = request.POST.get('mac_address')
                return render_to_response(
                    'registration_user_simple.html', 
                    { 'user_form': user_form, 
                      'user_profile_form': user_profile_form,
                      'mac_address': mac_address, },
                    context_instance=RequestContext(request))
    else:
        user_form = forms.UserForm()
        user_profile_form = forms.UserProfileForm()
        mac_address = request.GET.get('mac_address')

    return render_to_response(
        'registration_user_simple.html', 
        { 'user_form': user_form, 
          'user_profile_form': user_profile_form,
          'mac_address': mac_address, },
        context_instance=RequestContext(request))


def input_device_details(request, username='no_user'):

    # Mac address with GET method
    # Owner and admin from path + what they select in type
    #interfaces?
    #when username none when in demo mode or accessing directly by URL,
    # other option is to access through login
    
    if request.method == 'POST':
        device_form_data = request.POST.copy()
        device_form = forms.DeviceForm(request.POST)
        if device_form.is_valid():
            new_device = device_form.save(commit=False)
            if request.user.is_authenticated():
                new_device.admin = request.user
                new_device.owner = new_device.admin
                from_login = True
                new_device.save()
                return render_to_response('completed.html', {
                    'from_login': from_login, },
                    context_instance=RequestContext(request))

            elif device_form_data['username'] == 'no_user':
                new_device.admin = User.objects.get(username__exact='Demo')
                new_device.save()
                #make sure that a demo user always exists
                #currently username : Demo , pwd : demo, nickname : Demo
            else:
                new_device.admin = User.objects.get(username__exact=device_form_data['username'])
                new_device.owner = new_device.admin
                new_device.save()

            return render_to_response('completed.html',
                context_instance=RequestContext(request))
        else:
            logger.debug('Device form not valid! Form data_ ' + str(device_form_data))
            logger.debug('errors:' + str(device_form.errors))
            #device_form = forms.DeviceForm()
            mac_address = request.POST.get('mac_address')
            return render_to_response('registration_device.html', {
                'device_form': device_form, 'username': username,
                'mac_address': mac_address},
                context_instance=RequestContext(request))
    else:
        device_form = forms.DeviceForm()
        mac_address = request.GET.get('mac_address')
        print mac_address

    return render_to_response('registration_device.html', {
        'device_form': device_form, 'username': username,
        'mac_address': mac_address},
        context_instance=RequestContext(request))


def input_mac(request):
    return render_to_response('manual_MAC.html',
        context_instance=RequestContext(request))


def check_mac(request):
    if request.method == 'POST':
        mac_address = request.POST.get('mac_address')
        try:
            Device.objects.get(mac_address=mac_address)
            return HttpResponseRedirect(reverse(
            'django.contrib.auth.views.login'))
        except Device.DoesNotExist:
            return HttpResponseRedirect(reverse(
            'registration.views.registration',
            kwargs={'mac_address': mac_address }))



def registration(request, mac_address):
    return render_to_response('registration.html', {
        'mac_address': mac_address.lower(), },
        context_instance=RequestContext(request))


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next = request.POST.get('next')
                logger.debug( 'next: ' + next )
                if next == 'None' or next == None:
                    return render_to_response('welcome_download.html',
                        context_instance=RequestContext(request))

                mac_address = request.POST.get('mac_address')
                logger.debug("mac: " + mac_address )

                if mac_address != "" and mac_address != None:
                    return HttpResponseRedirect(next + user.username + '/?mac_address=' + mac_address)
                    #done with query string,would have been more general
                    #with regular expression
                else:
                    return HttpResponseRedirect(next)

            else:
                not_active = "True"
                next = request.POST.get('next')
                mac_address = request.POST.get('mac_address')
                return render_to_response('login.html', {'next': next,
                    'mac_address': mac_address, 'not_active': not_active},
                    context_instance=RequestContext(request))
        else:
            not_reg = "True"
            next = request.POST.get('next')
            mac_address = request.POST.get('mac_address')
            return render_to_response('login.html', {'next': next,
            'mac_address': mac_address, 'not_reg': not_reg},
            context_instance=RequestContext(request))
    else:
        next = request.GET.get('next')
        mac_address = request.GET.get('mac_address')
        return render_to_response( 'login.html', {'next': next, 'mac_address': mac_address},
        			   context_instance=RequestContext(request))

def log_out(request):
    logout(request)
    return render_to_response('main.html',
            context_instance=RequestContext(request))


def download(request):
    return render_to_response('welcome_download.html',
        context_instance=RequestContext(request))


def input_friends(request):
    return render_to_response('registration_friends.html', context_instance=RequestContext(request))


def phone_app(request):
    return render_to_response('phone_app.html', context_instance=RequestContext(request) )
