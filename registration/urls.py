from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',

    url(r'^start_page/$', 'registration.views.download'),
    url(r'^input_mac/$', 'registration.views.input_mac'),
    url(r'^check_mac/$', 'registration.views.check_mac'),
    url(r'^(?P<mac_address>([0-9A-Za-z]{2}[:\-]){5}([0-9A-Za-z]{2}))/$',
        'registration.views.registration'),
    url(r'^basic_details/$', 'registration.views.input_basic_user_details'),
    url(r'^login/$', 'registration.views.log_in'),
    url(r'^phone_details/$', 'registration.views.input_device_details'),
    url(r'^phone_details/(?P<username>\w{,255})/$',
        'registration.views.input_device_details'),
    url(r'^friends/$', 'registration.views.input_friends'),
    url(r'^phone_app/$', 'registration.views.phone_app'),
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
