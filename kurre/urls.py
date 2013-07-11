from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'kurre.views.home', name='home'),
	# url(r'^kurre/', include('kurre.foo.urls')),
	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# direct main requests to main template
	url(r'^$', direct_to_template, {'template': 'main.html'}),

	    
	url(r'^api/', include('core.urls')),
	url(r'^registration/', include ('registration.urls')),
	url(r'^event_log/$', 'events.views.index'),
	url(r'^event_log/events/$', 'events.views.events'),
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	url(r'^logout/$', 'registration.views.log_out'),
			   
			    
	
	# Uncomment the next line to enable the admin:
	url(r'^admin/core/interface_file/upload/$', 'core.admin_views.interface_file'),
	url(r'^admin/core/action_file/upload/$', 'core.admin_views.action_file'),
	url(r'^admin/core/schedule_file/upload/$', 'core.admin_views.schedule_file'),
	url(r'^admin/', include(admin.site.urls)),
	) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
