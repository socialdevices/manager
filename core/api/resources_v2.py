from core.models import DeviceInterface, Device, Interface, StateValue, Method, \
    MethodParameter
from resource_validations import DeviceInterfaceResourceValidation, \
    DeviceResourceValidation, DeviceStateValueResourceValidation
from django.conf.urls.defaults import url
from django.http import HttpResponseNotFound
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.http import HttpCreated
from tastypie.resources import ModelResource
from tastypie.utils import dict_strip_unicode_keys


class DeviceInterfaceResource(ModelResource):
    interface_name = fields.CharField(attribute='interface_name', null=True)
    
    class Meta:
        queryset = DeviceInterface.objects.all()
        resource_name = 'deviceinterface'
        authorization = Authorization()
        excludes = ['id']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        validation = DeviceInterfaceResourceValidation()
    
    def dispatch_detail(self, request, **kwargs):
    
        mac_address = kwargs.pop('mac_address')
        interface_name = kwargs.pop('interface_name')
        del kwargs['interface_resource_name']
        
        try:
            kwargs['pk'] = DeviceInterface.objects.get(device__mac_address=mac_address, interface__name=interface_name).id
        except DeviceInterface.DoesNotExist:
            return HttpResponseNotFound()
            
        return super(DeviceInterfaceResource, self).dispatch_detail(request, **kwargs)
    
    def post_list(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized))
        
        if 'mac_address' in kwargs:
            bundle.data['mac_address'] = kwargs['mac_address']
        
        self.is_valid(bundle, request)
        updated_bundle = self.obj_create(bundle, request=request)
        return HttpCreated(location=self.get_resource_uri(updated_bundle))
    
    def dehydrate(self, bundle):
        bundle.data['interface_name'] = bundle.obj.interface.name
        
        return bundle
    
    def hydrate(self, bundle):
        
        if 'mac_address' in bundle.data:
            bundle.obj.device = Device.objects.get(mac_address=bundle.data['mac_address'])
        
        if 'interface_name' in bundle.data:
            bundle.obj.interface = Interface.objects.get(name=bundle.data['interface_name'])
            
        return bundle
    
    # Override this method in order to select the objects for the nested resource
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
            
        qs_filters = super(DeviceInterfaceResource, self).build_filters(filters)
        
        # If device has been added to kwargs...
        if 'device' in filters:
            qs_filters['device'] = filters['device']
        
        return qs_filters
    
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': DeviceResource._meta.resource_name,
            'interface_resource_name': InterfaceResource._meta.resource_name,
        }
        
        if isinstance(bundle_or_obj, Bundle):
            kwargs['mac_address'] = bundle_or_obj.obj.device.mac_address
            kwargs['interface_name'] = bundle_or_obj.obj.interface.name
        else:
            kwargs['mac_address'] = bundle_or_obj.device.mac_address
            kwargs['interface_name'] = bundle_or_obj.interface.name
        
        if DeviceResource._meta.api_name is not None:
            kwargs['api_name'] = DeviceResource._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail_device_interface', kwargs = kwargs)
        

class InterfaceResource(ModelResource):
    name = fields.CharField(attribute='name', unique=True, help_text='The name of the interface')
    created_at = fields.DateTimeField(attribute='created_at', readonly=True, help_text='The date and time when the interface resource was created')
    updated_at = fields.DateTimeField(attribute='updated_at', readonly=True, help_text='The date and time when the interface resource was updated')
    
    class Meta:
        queryset = Interface.objects.all()
        resource_name = 'interface'
        authorization = Authorization()
        excludes = ['id', 'interface_file']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<name>(?!schema)[\w]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail_interface"),
        ]
    
    def dispatch_detail(self, request, **kwargs):
        
        interface_name = kwargs['name']
        try:
            kwargs['pk'] = Interface.objects.get(name=interface_name).id
        except Interface.DoesNotExist:
            return HttpResponseNotFound()
        
        return super(InterfaceResource, self).dispatch_detail(request, **kwargs)
    
    # Override this method in order to select the objects for the nested resource
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
            
        qs_filters = super(InterfaceResource, self).build_filters(filters)
        
        # If device has been added to kwargs...
        if 'device' in filters:
            qs_filters['deviceinterface__device'] = filters['device']
        
        return qs_filters
    
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }
        
        if isinstance(bundle_or_obj, Bundle):
            kwargs['name'] = bundle_or_obj.obj.name
        else:
            kwargs['name'] = bundle_or_obj.name
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail_interface', kwargs = kwargs)

class DeviceResource(ModelResource):
    mac_address = fields.CharField(attribute='mac_address', unique=True, help_text='A unique bluetooth mac address with a colon as the separator, e.g., aa:aa:aa:aa:aa:aa')
    name = fields.CharField(attribute='name', help_text='A human-readable device name')
    is_reserved = fields.BooleanField(attribute='is_reserved', help_text='A boolean value indicating whether the device is reserved, e.g., because it is executing an action')
    created_at = fields.DateTimeField(attribute='created_at', readonly=True, help_text='The date and time when the device resource was registered')
    updated_at = fields.DateTimeField(attribute='updated_at', readonly=True, help_text='The date and time when the device resource was updated')
    #interfaces = fields.ToManyField(InterfaceResource, 'interfaces', null=True, full=True)
    proximity_devices = fields.ListField(attribute='proximity_devices', null=True, help_text='A list of device mac addresses that are in proximity')
    
    class Meta:
        queryset = Device.objects.all()
        resource_name = 'device'
        authorization = Authorization()
        excludes = ['id']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        validation = DeviceResourceValidation()
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail_device"),
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/%s/$" % (self._meta.resource_name, InterfaceResource._meta.resource_name), self.wrap_view('dispatch_list_device_interface'), name="api_dispatch_list_device_interface"),
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/(?P<interface_resource_name>%s)/(?P<interface_name>[\w]+)/$" % (self._meta.resource_name, InterfaceResource._meta.resource_name), self.wrap_view('dispatch_detail_device_interface'), name="api_dispatch_detail_device_interface"),
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/(?P<interface_resource_name>%s)/(?P<interface_name>[\w]+)/method/$" % (self._meta.resource_name, InterfaceResource._meta.resource_name), self.wrap_view('dispatch_list_device_interface_method'), name="api_dispatch_list_device_interface_method"),
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/(?P<interface_resource_name>%s)/(?P<interface_name>[\w]+)/method/(?P<method_name>[\w]+)/$" % (self._meta.resource_name, InterfaceResource._meta.resource_name), self.wrap_view('dispatch_detail_device_interface_method'), name="api_dispatch_detail_device_interface_method"),
        ]
    
    def dispatch_detail(self, request, **kwargs):
        
        mac_address = kwargs['mac_address']
        try:
            kwargs['pk'] = Device.objects.get(mac_address=mac_address).id
        except Device.DoesNotExist:
            return HttpResponseNotFound()
        
        return super(DeviceResource, self).dispatch_detail(request, **kwargs)
    
    def dispatch_list_device_interface(self, request, **kwargs):
        
        if request.method == 'GET':
            mac_address = kwargs['mac_address']
            try:
                # self.cached_obj_get could also be used
                kwargs['device'] = Device.objects.get(mac_address=mac_address).id
            except Device.DoesNotExist:
                return HttpResponseNotFound()
        
        deviceinterface_resource = DeviceInterfaceResource()
        return deviceinterface_resource.dispatch_list(request, **kwargs)
    
    def dispatch_detail_device_interface(self, request, **kwargs):
        
        deviceinterface_resource = DeviceInterfaceResource()
        return deviceinterface_resource.dispatch_detail(request, **kwargs)
    
    def dispatch_list_device_interface_method(self, request, **kwargs):
        
        if request.method == 'GET':
            mac_address = kwargs.pop('mac_address')
            try:
                # self.cached_obj_get could also be used
                kwargs['device'] = Device.objects.get(mac_address=mac_address).id
            except Device.DoesNotExist:
                return HttpResponseNotFound()
            
            interface_name = kwargs.pop('interface_name')
            try:
                kwargs['interface'] = Interface.objects.get(name=interface_name).id
            except Interface.DoesNotExist:
                return HttpResponseNotFound()
        
        statevalue_resource = StateValueResource()
        return statevalue_resource.dispatch_list(request, **kwargs)
    
    def dispatch_detail_device_interface_method(self, request, **kwargs):
        
        statevalue_resource = StateValueResource()
        return statevalue_resource.dispatch_detail(request, **kwargs)
    
    def dehydrate(self, bundle):
        proximity_devices = bundle.obj.get_proximity_mac_addresses()
        
        bundle.data['proximity_devices'] = []
        
        for device in proximity_devices:
            bundle.data['proximity_devices'].append(device)
        
        return bundle
    
    def hydrate(self, bundle):

        if bundle.obj.mac_address:
            if 'proximity_devices' in bundle.data:
                bundle.obj.set_proximity_devices(bundle.data['proximity_devices'])
        
        return bundle
    
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }
        
        if isinstance(bundle_or_obj, Bundle):
            kwargs['mac_address'] = bundle_or_obj.obj.mac_address
        else:
            kwargs['mac_address'] = bundle_or_obj.mac_address
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail_device', kwargs = kwargs)

#class MethodResource(ModelResource):
#    #interface = fields.ToOneField(InterfaceResource, 'interface')    
#    
#    class Meta:
#        queryset = Method.objects.all()
#        resource_name = 'method'
#        authorization = Authorization()
#        excludes = ['id', 'created_at', 'updated_at']
#        include_resource_uri = False

class StateValueResource(ModelResource):
    
    #device = fields.ForeignKey(DeviceResource, 'device')
    #interface = fields.ForeignKey(InterfaceResource, 'interface')
    #method = fields.ForeignKey(MethodResource, 'method')
    #mac_address = fields.CharField(attribute='mac_address', null=True)
    #interface_name = fields.CharField(attribute='interface_name', null=True)
    method_name = fields.CharField(attribute='method_name', null=True)
    value = fields.CharField(attribute='value')
    arguments = fields.DictField(attribute="arguments", null=True)
    
    class Meta:
        queryset = StateValue.objects.all()
        resource_name = 'state_value'
        authorization = Authorization()
        excludes = ['id']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        validation = DeviceStateValueResourceValidation()
        
    def dispatch_detail(self, request, **kwargs):
    
        mac_address = kwargs.pop('mac_address')
        interface_name = kwargs.pop('interface_name')
        method_name = kwargs.pop('method_name')
        del kwargs['interface_resource_name']
        
        try:
            kwargs['pk'] = StateValue.objects.get(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).id
        except StateValue.DoesNotExist:
            return HttpResponseNotFound()
            
        return super(StateValueResource, self).dispatch_detail(request, **kwargs)
    
    def post_list(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized))
        
        if 'mac_address' in kwargs:
            bundle.data['mac_address'] = kwargs['mac_address']
        
        if 'interface_name' in kwargs:
            bundle.data['interface_name'] = kwargs['interface_name']
        
        self.is_valid(bundle, request)
        updated_bundle = self.obj_create(bundle, request=request)
        return HttpCreated(location=self.get_resource_uri(updated_bundle))
    
    # Override this method in order to select the objects for the nested resource
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
            
        qs_filters = super(StateValueResource, self).build_filters(filters)
        
        # If device has been added to kwargs...
        if 'device' in filters:
            qs_filters['device'] = filters['device']
        
        if 'interface' in filters:
            qs_filters['method__interface'] = filters['interface']
        
        return qs_filters
    
    def dehydrate(self, bundle):
        bundle.data['method_name'] = bundle.obj.method.name
        
        bundle.data['arguments'] = {}
        for argument in bundle.obj.statevalueargument_set.all():
            bundle.data['arguments'][argument.method_parameter.name] = argument.value
        
        return bundle
    
    def hydrate(self, bundle):
        
        if 'mac_address' in bundle.data:
            bundle.obj.device = Device.objects.get(mac_address=bundle.data['mac_address'])
        
        if 'interface_name' in bundle.data and 'method_name' in bundle.data:
            bundle.obj.method = Method.objects.get(interface__name=bundle.data['interface_name'], name=bundle.data['method_name'])
        
        if 'arguments' in bundle.data:
            bundle.obj.arguments = bundle.data['arguments']
        
        return bundle
    
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': DeviceResource._meta.resource_name,
            'interface_resource_name': InterfaceResource._meta.resource_name,
        }
        
        if isinstance(bundle_or_obj, Bundle):
            kwargs['mac_address'] = bundle_or_obj.obj.device.mac_address
            kwargs['interface_name'] = bundle_or_obj.obj.method.interface.name
            kwargs['method_name'] = bundle_or_obj.obj.method.name
        else:
            kwargs['mac_address'] = bundle_or_obj.device.mac_address
            kwargs['interface_name'] = bundle_or_obj.method.interface.name
            kwargs['method_name'] = bundle_or_obj.method.name
        
        if DeviceResource._meta.api_name is not None:
            kwargs['api_name'] = DeviceResource._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail_device_interface_method', kwargs = kwargs)
    
#    def hydrate(self, bundle):
#        if 'mac_address' in bundle.data:
#            bundle.obj.device = Device.objects.get(mac_address=bundle.data['mac_address']) # only mac_address here
#        
#        if 'interface_name' in bundle.data:
#            bundle.obj.interface = bundle.obj.device.interfaces.get(name=bundle.data['interface_name'])
#        
#        if 'method_name' in bundle.data:
#            bundle.obj.method = Method.objects.get(interface=bundle.obj.interface, name=bundle.data['method_name']) #bundle.obj.interface.methods.get(name=bundle.data['method_name'])
#            
#        return bundle
            
#    def override_urls(self):
#        return [
#            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/(?P<interface_name>[\w]+)/(?P<method_name>[\w]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail_state_value'), name="api_dispatch_detail_state_value"), #[0-9a-fA-F:]+
#        ]
    
#    def dispatch_detail_state_value(self, request, **kwargs):
#        mac_address = kwargs.pop('mac_address')
#        interface_name = kwargs.pop('interface_name')
#        method_name = kwargs.pop('method_name')
#        
#        #bundle.data['mac_address'] = mac_address
#        #bundle.data['interface_name'] = interface_name
#        #bundle.data['method_name'] = method_name
#        
#        #device = get_object_or_404(Device, mac_address=mac_address) #kwargs['device'] = get_object_or_404(Device, mac_address=mac_address)
#        #interface = get_object_or_404(device.interfaces, name=interface_name) #kwargs['interface'] = get_object_or_404(kwargs['device'].interfaces, name=interface_name)
#        #method = get_object_or_404(Method, interface=interface, name=method_name) #kwargs['method'] = get_object_or_404(Method, interface=kwargs['interface'], name=method_name)
#        kwargs['pk'] = get_object_or_404(StateValue, device__mac_address=mac_address, interface__name=interface_name, method__name=method_name).id #get_object_or_404(StateValue, device=device, interface=interface, method=method).id
#        
#        return super(StateValueResource, self).dispatch_detail(request, **kwargs)
