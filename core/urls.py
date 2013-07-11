from core.api import resources_v1, resources_v2, resources_v3
from django.conf.urls import patterns, url, include
from tastypie.api import Api
import haystack

api_v1 = Api(api_name='v1')
api_v1.register(resources_v1.DeviceResource())
api_v1.register(resources_v1.InterfaceResource())
api_v1.register(resources_v1.StateValueResource())
api_v1.register(resources_v1.MethodResource())

api_v2 = Api(api_name='v2')
api_v2.register(resources_v2.DeviceResource())
api_v2.register(resources_v2.InterfaceResource())

api_v3 = Api(api_name='v3')
api_v3.register(resources_v3.ActionResource())
api_v3.register(resources_v3.RoleResource())
api_v3.register(resources_v3.InterfaceResource())
api_v3.register(resources_v3.MethodResource())
api_v3.register(resources_v3.DeviceResource())

urlpatterns = patterns('',
    url(r'^', include(api_v1.urls)),
    url(r'^', include(api_v2.urls)),
    url(r'^', include(api_v3.urls)),
    url(r'^interface_file/$', 'core.views.parse_interfaces'),
    url(r'^action_file/$', 'core.views.parse_actions'),
    url(r'^schedule_file/$', 'core.views.parse_schedules'),
    url(r'^configuration/$', 'core.views.get_configuration'),
    url(r'^search/', include('haystack.urls')),
)
