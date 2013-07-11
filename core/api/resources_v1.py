from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from core.models import Device, Interface, StateValue, Method, DeviceInterface
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404

#class ProximityGroupResource(ModelResource):
#    num_devices = fields.IntegerField(attribute='num_devices', readonly=True)
#    devices = fields.ToManyField('core.resources.DeviceResource', 'device_set', related_name='proximity_group')
#    
#    class Meta:
#        queryset = ProximityGroup.objects.all()
#        resource_name = 'proximity_group'
#        authorization = Authorization()
#        excludes = ['created_at', 'updated_at']
#        include_resource_uri = False
#    
#    def dehydrate(self, bundle):
#        try:
#            devices = bundle.obj.device_set.all()
#        except ProximityGroup.DoesNotExist:
#            devices = False
#        
#        if devices:
#            bundle.data['devices'] = []
#            for device in devices:
#                bundle.data['devices'].append(device.mac_address)
#        
#        return bundle
#    
#    def hydrate(self, bundle):
#        print 'moi'
#        if 'devices' in bundle.data:
#            bundle.obj.device_set.clear()
#            print 'jee'
#            for mac_address in bundle.data['devices']:
#                print mac_address
#                bundle.obj.device_set.add(Device.objects.get(mac_address=mac_address))
#        
#        return bundle

class InterfaceResource(ModelResource):
    methods = fields.ToManyField('core.resources.MethodResource', 'method_set', related_name='interface', null=True, full=True)
    
    class Meta:
        queryset = Interface.objects.all()
        resource_name = 'interface'
        authorization = Authorization()
        excludes = ['id', 'created_at', 'updated_at']
        include_resource_uri = False
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<name>[\w]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail_interface'), name="api_dispatch_detail_interface"),
        ]
    
    def dispatch_detail_interface(self, request, **kwargs):
        name = kwargs.pop('name')
        
        kwargs['pk'] = get_object_or_404(Interface, name=name).id
        
        return super(InterfaceResource, self).dispatch_detail(request, **kwargs)
    
    def save_m2m(self, bundle):
         
        for method in bundle.data['methods']:
            bundle.obj.method_set.create(name=method.obj.name)

class DeviceResource(ModelResource):
    #created_at = fields.DateTimeField(null=True)
    #mac_address = fields.CharField(unique=True)
    #proximity_group = fields.ForeignKey(ProximityGroupResource, 'proximity_group', null=True, full=True)
    #interface = fields.ToManyField('core.resources.InterfaceResource', 'interface_set', related_name='interface')
    interfaces = fields.ToManyField(InterfaceResource, 'interfaces', null=True, full=True)
    proximity_devices = fields.ListField(attribute='proximity_devices', null=True)
    
    class Meta:
        queryset = Device.objects.all()
        resource_name = 'device'
        authorization = Authorization()
        excludes = ['id', 'created_at', 'updated_at']
        include_resource_uri = False
    
    def save_m2m(self, bundle):
        for interface in bundle.data['interfaces']:
            DeviceInterface.objects.create(device=bundle.obj, interface=interface.obj)
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/$" % self._meta.resource_name, self.wrap_view('dispatch_detail_device'), name="api_dispatch_detail_device"),
            #url(r"^(?P<resource_name>%s)/(?P<>)),
        ]
    
    def dispatch_detail_device(self, request, **kwargs):
        mac_address = kwargs.pop('mac_address')
        
        kwargs['pk'] = get_object_or_404(Device, mac_address=mac_address).id
        
        return super(DeviceResource, self).dispatch_detail(request, **kwargs)
    
    def dehydrate(self, bundle):
        devices = bundle.obj.get_proximity_mac_addresses()
        
        
        bundle.data['proximity_devices'] = []
        
        for device in devices:
            bundle.data['proximity_devices'].append(device)
        
        return bundle
    
    def hydrate(self, bundle):

        if bundle.obj.mac_address:
            if 'devices' in bundle.data:
                bundle.obj.set_proximity_devices(bundle.data['devices'])
        
        return bundle

class MethodResource(ModelResource):
    #interface = fields.ToOneField(InterfaceResource, 'interface')    
    
    class Meta:
        queryset = Method.objects.all()
        resource_name = 'method'
        authorization = Authorization()
        excludes = ['id', 'created_at', 'updated_at']
        include_resource_uri = False

class StateValueResource(ModelResource):
    
    #device = fields.ForeignKey(DeviceResource, 'device')
    #interface = fields.ForeignKey(InterfaceResource, 'interface')
    #method = fields.ForeignKey(MethodResource, 'method')
    mac_address = fields.CharField(attribute='mac_address', null=True)
    interface_name = fields.CharField(attribute='interface_name', null=True)
    method_name = fields.CharField(attribute='method_name', null=True)
    
    class Meta:
        queryset = StateValue.objects.all()
        resource_name = 'state_value'
        authorization = Authorization()
        excludes = ['id', 'created_at', 'updated_at']
        include_resource_uri = False
    
    def dehydrate(self, bundle):
        bundle.data['mac_address'] = bundle.obj.device.mac_address
        bundle.data['interface_name'] = bundle.obj.method.interface.name
        bundle.data['method_name'] = bundle.obj.method.name
        
        return bundle
    
    def hydrate(self, bundle):
        if 'mac_address' in bundle.data:
            bundle.obj.device = Device.objects.get(mac_address=bundle.data['mac_address']) # only mac_address here
        
        if 'interface_name' in bundle.data and 'method_name' in bundle.data:
            bundle.obj.method = Method.objects.get(interface__name=bundle.data['interface_name'], name=bundle.data['method_name']) #bundle.obj.interface.methods.get(name=bundle.data['method_name'])
            
        return bundle
            
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<mac_address>(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2})/(?P<interface_name>[\w]+)/(?P<method_name>[\w]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail_state_value'), name="api_dispatch_detail_state_value"), #[0-9a-fA-F:]+
        ]
    
    def dispatch_detail_state_value(self, request, **kwargs):
        mac_address = kwargs.pop('mac_address')
        interface_name = kwargs.pop('interface_name')
        method_name = kwargs.pop('method_name')
        
        #bundle.data['mac_address'] = mac_address
        #bundle.data['interface_name'] = interface_name
        #bundle.data['method_name'] = method_name
        
        #device = get_object_or_404(Device, mac_address=mac_address) #kwargs['device'] = get_object_or_404(Device, mac_address=mac_address)
        #interface = get_object_or_404(device.interfaces, name=interface_name) #kwargs['interface'] = get_object_or_404(kwargs['device'].interfaces, name=interface_name)
        #method = get_object_or_404(Method, interface=interface, name=method_name) #kwargs['method'] = get_object_or_404(Method, interface=kwargs['interface'], name=method_name)
        kwargs['pk'] = get_object_or_404(StateValue, device__mac_address=mac_address, interface__name=interface_name, method__name=method_name).id #get_object_or_404(StateValue, device=device, interface=interface, method=method).id
        
        return super(StateValueResource, self).dispatch_detail(request, **kwargs)
