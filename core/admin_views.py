from core.forms import UploadInterfaceFileForm, UploadActionFileForm, \
    UploadScheduleFileForm
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
from events.event import EventHandler
import logging

logger = logging.getLogger(__name__)

def interface_file(request):
    if request.method == 'POST':
        form = UploadInterfaceFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                form.save()
            except Exception, e:
                return HttpResponseServerError(e)
            
            event_handler = EventHandler()
            event_handler.add_event(u'Interface file %s was uploaded and parsed successfully' % form.cleaned_data['file'].name)
            logger.debug(u'Interface file %s was uploaded and parsed successfully' % form.cleaned_data['file'].name)
            
            return HttpResponseRedirect(reverse('admin:core_interface_changelist'))
    else:
        form = UploadInterfaceFileForm()
    
    return render_to_response(
        "admin/core/file_upload.html", {
            'title': 'Upload interface file',
            'app_label': 'core',
            'file_name': 'interface file',
            'form_url': reverse(interface_file),
            'form_id': 'interface_file_form',
            'form': form,
        }, RequestContext(request, {}),
    )
interface_file = staff_member_required(interface_file)


def action_file(request):
    if request.method == 'POST':
        form = UploadActionFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                form.save()
            except Exception, e:
                return HttpResponseServerError(e)
            
            event_handler = EventHandler()
            event_handler.add_event(u'Action file %s was uploaded and parsed successfully' % form.cleaned_data['file'].name)
            logger.debug(u'Action file %s was uploaded and parsed successfully' % form.cleaned_data['file'].name)
            
            return HttpResponseRedirect(reverse('admin:core_action_changelist'))
    else:
        form = UploadActionFileForm()
    
    return render_to_response(
        "admin/core/file_upload.html", {
            'title': 'Upload action file',
            'app_label': 'core',
            'file_name': 'action file',
            'form_url': reverse(action_file),
            'form_id': 'interface_file_form',
            'form': form,
        }, RequestContext(request, {}),
    )
action_file = staff_member_required(action_file)



def schedule_file(request):
    if request.method == 'POST':
        form = UploadScheduleFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                form.save()           
            except Exception, e:
                return HttpResponseServerError(e)
            
            event_handler = EventHandler()
            event_handler.add_event(u'Schedule file %s was uploaded and parsed successfully' % form.cleaned_data['file'].name)
            
            return HttpResponseRedirect(reverse('admin:core_schedule_changelist'))
    else:
        form = UploadScheduleFileForm()
    
    return render_to_response(
        "admin/core/file_upload.html", {
            'title': 'Upload schedule file',
            'app_label': 'core',
            'file_name': 'schedule file',
            'form_url': reverse(schedule_file),
            'form_id': 'schedule_file_form',
            'form': form,
        }, RequestContext(request, {}),
    )
schedule_file = staff_member_required(schedule_file)
