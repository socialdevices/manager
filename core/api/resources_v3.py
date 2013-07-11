from core.api.serializers import CamelCaseJSONSerializer
from core.models import Action, ActionDevice, Interface, ActionDeviceInterface, \
    Method, Device, DeviceInterface, StateValue
from django.conf.urls import url
from haystack.query import SearchQuerySet
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
import logging

logger = logging.getLogger(__name__)


class ActionResource(ModelResource):
    #roles = fields.ToManyField('core.api.resources_v3.RoleResource', 'actiondevice_set', related_name='action')
    roles_uri = fields.CharField(attribute='roles_uri', null=True,
                                 readonly=True, help_text="Roles URI")
    parameters = fields.ListField(attribute='parameters', null=True,
                                  blank=True, readonly=True, help_text="Action parameters")

    class Meta:
        queryset = Action.objects.all()
        resource_name = 'actions'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        excludes = ['precondition_expression', 'action_file']

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>{0})/'
                '(?P<role_resource_name>{1})/'
                'schema{2}$'.format(self._meta.resource_name,
                                    RoleResource._meta.resource_name,
                                    trailing_slash()),
                self.wrap_view('get_action_roles_schema'),
                name='api_get_action_roles_schema'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<action_id>\w[\w/-]*)/'
                '(?P<role_resource_name>{1}){2}$'.format(self._meta.resource_name,
                                                         RoleResource._meta.resource_name,
                                                         trailing_slash()),
                self.wrap_view('dispatch_list_action_roles'),
                name='api_dispatch_list_action_roles'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<action_id>\w[\w/-]*)/'
                '(?P<role_resource_name>{1})/'
                '(?P<role_id>\w[\w/-]*){2}$'.format(self._meta.resource_name,
                                                    RoleResource._meta.resource_name,
                                                    trailing_slash()),
                self.wrap_view('dispatch_detail_action_roles'),
                name='api_dispatch_detail_action_roles'),
        ]

    def get_action_roles_schema(self, request, **kwargs):
        action_roles_resource = ActionRolesResource()
        return action_roles_resource.get_schema(request, **kwargs)

    def dispatch_list_action_roles(self, request, **kwargs):
        action_roles_resource = ActionRolesResource()
        return action_roles_resource.dispatch_list(request, **kwargs)

    def dispatch_detail_action_roles(self, request, **kwargs):
        action_roles_resource = ActionRolesResource()
        return action_roles_resource.dispatch_detail(request, **kwargs)

    def dehydrate_roles_uri(self, bundle):
        kwargs = {'resource_name': self._meta.resource_name,
                  'role_resource_name': RoleResource._meta.resource_name,
                  'action_id': bundle.obj.pk,
                  'api_name': RoleResource._meta.api_name}
        roles_uri = self._build_reverse_url('api_dispatch_list_action_roles',
                                            kwargs=kwargs)

        return roles_uri

    def dehydrate_parameters(self, bundle):
        parameters = bundle.obj.actionparameter_set.values_list('name', flat=True).order_by('parameter_position')

        return list(parameters)


class RoleResource(ModelResource):
#    interfaces = fields.ToManyField('core.api.resources_v3.InterfaceResource',
#                                    'interfaces')
    action = fields.ToOneField(ActionResource, 'action')
    # TODO: remove null=True
    interfaces_uri = fields.CharField(attribute='interfaces_uri', null=True,
                                      readonly=True, help_text="Interfaces URI")

    class Meta:
        queryset = ActionDevice.objects.all()
        resource_name = 'roles'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>{0})/'
                '(?P<interface_resource_name>{1})/'
                'schema{2}$'.format(self._meta.resource_name,
                                    InterfaceResource._meta.resource_name,
                                    trailing_slash()),
                self.wrap_view('get_role_interfaces_schema'),
                name='api_get_role_interfaces_schema'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<role_id>\w[\w/-]*)/'
                '(?P<interface_resource_name>{1}){2}$'.format(self._meta.resource_name,
                                                              InterfaceResource._meta.resource_name,
                                                              trailing_slash()),
                self.wrap_view('dispatch_list_role_interfaces'),
                name='api_dispatch_list_role_interfaces'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<role_id>\w[\w/-]*)/'
                '(?P<interface_resource_name>{1})/'
                '(?P<interface_id>\w[\w/-]*){2}$'.format(self._meta.resource_name,
                                                         InterfaceResource._meta.resource_name,
                                                         trailing_slash()),
                self.wrap_view('dispatch_detail_role_interfaces'),
                name='api_dispatch_detail_role_interfaces'),
        ]

    def get_role_interfaces_schema(self, request, **kwargs):
        role_interfaces_resource = RoleInterfacesResource()
        return role_interfaces_resource.get_schema(request, **kwargs)

    def dispatch_list_role_interfaces(self, request, **kwargs):
        role_interfaces_resource = RoleInterfacesResource()
        return role_interfaces_resource.dispatch_list(request, **kwargs)

    def dispatch_detail_role_interfaces(self, request, **kwargs):
        role_interfaces_resource = RoleInterfacesResource()
        return role_interfaces_resource.dispatch_detail(request, **kwargs)

    def dehydrate_interfaces_uri(self, bundle):
        kwargs = {'resource_name': self._meta.resource_name,
                  'interface_resource_name': InterfaceResource._meta.resource_name,
                  'role_id': bundle.obj.pk,
                  'api_name': self._meta.api_name}
        interfaces_uri = self._build_reverse_url('api_dispatch_list_role_interfaces',
                                                 kwargs=kwargs)

        return interfaces_uri


class ActionRolesResource(ModelResource):
    action = fields.ToOneField(ActionResource, 'action')
    role = fields.CharField(attribute='role_uri', null=True,
                            readonly=True, help_text="Role URI")

    class Meta:
        queryset = ActionDevice.objects.all()
        resource_name = 'actionroles'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        excludes = ['id', 'name', 'parameter_position', 'updated_at']
        include_resource_uri = False

    def dehydrate_role(self, bundle):
        kwargs = {'resource_name': RoleResource._meta.resource_name,
                  'pk': bundle.obj.pk,
                  'api_name': RoleResource._meta.api_name}
        role_uri = self._build_reverse_url('api_dispatch_detail',
                                           kwargs=kwargs)

        return role_uri

    def dispatch_detail(self, request, **kwargs):
        role_id = kwargs.pop('role_id')
        del kwargs['role_resource_name']

        kwargs['pk'] = role_id

        return super(ActionRolesResource, self).dispatch_detail(request, **kwargs)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        qs_filters = super(ActionRolesResource, self).build_filters(filters)

        if 'action_id' in filters:
            qs_filters['action_id'] = filters['action_id']

        return qs_filters

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': ActionResource._meta.resource_name,
            'role_resource_name': RoleResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['action_id'] = bundle_or_obj.obj.action.id
            kwargs['role_id'] = bundle_or_obj.obj.id
        else:
            kwargs['action_id'] = bundle_or_obj.action.id
            kwargs['role_id'] = bundle_or_obj.id

        if RoleResource._meta.api_name is not None:
            kwargs['api_name'] = RoleResource._meta.api_name

        return self._build_reverse_url('api_dispatch_detail_action_roles',
                                       kwargs=kwargs)


class InterfaceResource(ModelResource):
    methods_uri = fields.CharField(attribute='methods_uri', null=True,
                                   readonly=True, help_text="Methods URI")

    class Meta:
        queryset = Interface.objects.all()
        resource_name = 'interfaces'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        excludes = ['interface_file']

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>{0})/'
                '(?P<method_resource_name>{1})/'
                'schema{2}$'.format(self._meta.resource_name,
                                    MethodResource._meta.resource_name,
                                    trailing_slash()),
                self.wrap_view('get_interface_methods_schema'),
                name='api_get_interface_methods_schema'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<interface_id>\w[\w/-]*)/'
                '(?P<method_resource_name>{1}){2}$'.format(self._meta.resource_name,
                                                           MethodResource._meta.resource_name,
                                                           trailing_slash()),
                self.wrap_view('dispatch_list_interface_methods'),
                name='api_dispatch_list_interface_methods'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<interface_id>\w[\w/-]*)/'
                '(?P<method_resource_name>{1})/'
                '(?P<method_id>\w[\w/-]*){2}$'.format(self._meta.resource_name,
                                                      MethodResource._meta.resource_name,
                                                      trailing_slash()),
                self.wrap_view('dispatch_detail_interface_methods'),
                name='api_dispatch_detail_interface_methods'),
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def get_interface_methods_schema(self, request, **kwargs):
        interface_methods_resource = InterfaceMethodsResource()
        return interface_methods_resource.get_schema(request, **kwargs)

    def dispatch_list_interface_methods(self, request, **kwargs):
        interface_methods_resource = InterfaceMethodsResource()
        return interface_methods_resource.dispatch_list(request, **kwargs)

    def dispatch_detail_interface_methods(self, request, **kwargs):
        interface_methods_resource = InterfaceMethodsResource()
        return interface_methods_resource.dispatch_detail(request, **kwargs)

    def dehydrate_methods_uri(self, bundle):
        kwargs = {'resource_name': self._meta.resource_name,
                  'method_resource_name': MethodResource._meta.resource_name,
                  'interface_id': bundle.obj.pk,
                  'api_name': RoleResource._meta.api_name}
        methods_uri = self._build_reverse_url('api_dispatch_list_interface_methods',
                                              kwargs=kwargs)

        return methods_uri
 

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query. 
        q = request.GET.get('q','')
 
        try:
            results = SearchQuerySet().auto_query(q)
        except IndexError:
            results = None

        objects = []

        logger.debug( 'results for query: {0}, {1}, pcs'.format( q, results ) )

        i=0
        if results:
            for result in results:
                bundle = self.build_bundle(obj=result.object, request=request)
                bundle = self.full_dehydrate(bundle)
                objects.append(bundle)
        
        object_list = {
            'objects': objects,
        }

        return self.create_response(request, object_list)


class RoleInterfacesResource(ModelResource):
    role = fields.ToOneField(RoleResource, 'action_device')
    interface = fields.ToOneField(InterfaceResource, 'interface')

    class Meta:
        queryset = ActionDeviceInterface.objects.all()
        resource_name = 'roleinterfaces'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        excludes = ['id']
        include_resource_uri = False

    def dispatch_detail(self, request, **kwargs):
        role_id = kwargs.pop('role_id')
        del kwargs['interface_resource_name']

        kwargs['action_device_id'] = role_id

        return super(RoleInterfacesResource, self).dispatch_detail(request, **kwargs)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        qs_filters = super(RoleInterfacesResource, self).build_filters(filters)

        if 'role_id' in filters:
            qs_filters['action_device'] = filters['role_id']

        return qs_filters

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': RoleResource._meta.resource_name,
            'interface_resource_name': InterfaceResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['role_id'] = bundle_or_obj.obj.action_device.id
            kwargs['interface_id'] = bundle_or_obj.obj.interface.id
        else:
            kwargs['role_id'] = bundle_or_obj.action_device.id
            kwargs['interface_id'] = bundle_or_obj.interface.id

        if RoleResource._meta.api_name is not None:
            kwargs['api_name'] = RoleResource._meta.api_name

        return self._build_reverse_url('api_dispatch_detail_role_interfaces',
                                       kwargs=kwargs)


class MethodResource(ModelResource):
    interface = fields.ToOneField(InterfaceResource, 'interface')
    parameters = fields.ListField(attribute='parameters', null=True,
                                  blank=True, readonly=True, help_text="Method parameters")

    class Meta:
        queryset = Method.objects.all()
        resource_name = 'methods'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    def dehydrate_parameters(self, bundle):
        parameters = bundle.obj.methodparameter_set.values_list('name', flat=True)

        return list(parameters)


class InterfaceMethodsResource(ModelResource):
    interface = fields.ToOneField(InterfaceResource, 'interface')
    method = fields.CharField(attribute='method_uri', null=True,
                              readonly=True, help_text="Method URI")

    class Meta:
        queryset = Method.objects.all()
        resource_name = 'interfacemethods'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        excludes = ['id', 'name', 'updated_at']
        include_resource_uri = False

    def dehydrate_method(self, bundle):
        kwargs = {'resource_name': MethodResource._meta.resource_name,
                  'pk': bundle.obj.pk,
                  'api_name': MethodResource._meta.api_name}
        method_uri = self._build_reverse_url('api_dispatch_detail',
                                           kwargs=kwargs)

        return method_uri

    def dispatch_detail(self, request, **kwargs):
        method_id = kwargs.pop('method_id')
        del kwargs['method_resource_name']

        kwargs['pk'] = method_id

        return super(InterfaceMethodsResource, self).dispatch_detail(request, **kwargs)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        qs_filters = super(InterfaceMethodsResource, self).build_filters(filters)

        if 'interface_id' in filters:
            qs_filters['interface_id'] = filters['interface_id']

        return qs_filters

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': InterfaceResource._meta.resource_name,
            'method_resource_name': MethodResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['interface_id'] = bundle_or_obj.obj.interface.id
            kwargs['method_id'] = bundle_or_obj.obj.id
        else:
            kwargs['interface_id'] = bundle_or_obj.interface.id
            kwargs['method_id'] = bundle_or_obj.id

        if MethodResource._meta.api_name is not None:
            kwargs['api_name'] = MethodResource._meta.api_name

        return self._build_reverse_url('api_dispatch_detail_interface_methods',
                                       kwargs=kwargs)


class DeviceResource(ModelResource):
    id_string = fields.CharField(attribute='_get_id_string', readonly=True)
    interfaces_uri = fields.CharField(attribute='interfaces_uri', null=True,
                                      readonly=True, help_text="Interfaces URI")
    states_uri = fields.CharField(attribute='states_uri', null=True,
                                  readonly=True, help_text="States URI")

    class Meta:
        queryset = Device.objects.all()
        resource_name = 'devices'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'patch', 'delete']
        excludes = ['type']

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>{0})/'
                '(?P<interface_resource_name>{1})/'
                'schema{2}$'.format(self._meta.resource_name,
                                    InterfaceResource._meta.resource_name,
                                    trailing_slash()),
                self.wrap_view('get_device_interfaces_schema'),
                name='api_get_device_interfaces_schema'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<device_id>\w[\w/-]*)/'
                '(?P<interface_resource_name>{1}){2}$'.format(self._meta.resource_name,
                                                              InterfaceResource._meta.resource_name,
                                                              trailing_slash()),
                self.wrap_view('dispatch_list_device_interfaces'),
                name='api_dispatch_list_device_interfaces'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<device_id>\w[\w/-]*)/'
                '(?P<interface_resource_name>{1})/'
                '(?P<interface_id>\w[\w/-]*){2}$'.format(self._meta.resource_name,
                                                         InterfaceResource._meta.resource_name,
                                                         trailing_slash()),
                self.wrap_view('dispatch_detail_device_interfaces'),
                name='api_dispatch_detail_device_interfaces'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<state_resource_name>{1})/'
                'schema{2}$'.format(self._meta.resource_name,
                                    DeviceStateValueResource._meta.resource_name,
                                    trailing_slash()),
                self.wrap_view('get_device_states_schema'),
                name='api_get_device_states_schema'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<device_id>\w[\w/-]*)/'
                '(?P<state_resource_name>{1}){2}$'.format(self._meta.resource_name,
                                                          DeviceStateValueResource._meta.resource_name,
                                                          trailing_slash()),
                self.wrap_view('dispatch_list_device_states'),
                name='api_dispatch_list_device_states'),
            url(r'^(?P<resource_name>{0})/'
                '(?P<device_id>\w[\w/-]*)/'
                '(?P<state_resource_name>{1})/'
                '(?P<method_id>\w[\w/-]*){2}$'.format(self._meta.resource_name,
                                                      DeviceStateValueResource._meta.resource_name,
                                                      trailing_slash()),
                self.wrap_view('dispatch_detail_device_states'),
                name='api_dispatch_detail_device_states'),
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def get_device_interfaces_schema(self, request, **kwargs):
        device_interfaces_resource = DeviceInterfacesResource()
        return device_interfaces_resource.get_schema(request, **kwargs)

    def dispatch_list_device_interfaces(self, request, **kwargs):
        device_interfaces_resource = DeviceInterfacesResource()
        return device_interfaces_resource.dispatch_list(request, **kwargs)

    def dispatch_detail_device_interfaces(self, request, **kwargs):
        device_interfaces_resource = DeviceInterfacesResource()
        return device_interfaces_resource.dispatch_detail(request, **kwargs)

    def get_device_states_schema(self, request, **kwargs):
        device_states_resource = DeviceStateValueResource()
        return device_states_resource.get_schema(request, **kwargs)

    def dispatch_list_device_states(self, request, **kwargs):
        device_states_resource = DeviceStateValueResource()
        return device_states_resource.dispatch_list(request, **kwargs)

    def dispatch_detail_device_states(self, request, **kwargs):
        device_states_resource = DeviceStateValueResource()
        return device_states_resource.dispatch_detail(request, **kwargs)
    
    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query. 
        q = request.GET.get('q','')
        limits = request.GET.get('limit', '')
        limit = 1
        try:
            limit = int( limits )  
        except ValueError:
            limit = -1     
        try:
            results = SearchQuerySet().auto_query(q)
        except IndexError:
            results = None

        objects = []

        logger.debug( 'results for query: {0}, {1}, pcs'.format( q, results ) )

        i=0
        if results:
            for result in results:
                if i == limit:
                    break
                bundle = self.build_bundle(obj=result.object, request=request)
                bundle = self.full_dehydrate(bundle)
                objects.append(bundle)
                i+=1
        
        object_list = {
            'objects': objects,
        }

        return self.create_response(request, object_list)

    def dehydrate_states_uri(self, bundle):
        kwargs = {'resource_name': self._meta.resource_name,
                  'state_resource_name': DeviceStateValueResource._meta.resource_name,
                  'device_id': bundle.obj.pk,
                  'api_name': self._meta.api_name}
        interfaces_uri = self._build_reverse_url('api_dispatch_list_device_states',
                                                 kwargs=kwargs)

        return interfaces_uri


    def dehydrate_interfaces_uri(self, bundle):
        kwargs = {'resource_name': self._meta.resource_name,
                  'interface_resource_name': InterfaceResource._meta.resource_name,
                  'device_id': bundle.obj.pk,
                  'api_name': self._meta.api_name}
        interfaces_uri = self._build_reverse_url('api_dispatch_list_device_interfaces',
                                                 kwargs=kwargs)

        return interfaces_uri



class DeviceInterfacesResource(ModelResource):
    device = fields.ToOneField(DeviceResource, 'device')
    interface = fields.ToOneField(InterfaceResource, 'interface')

    class Meta:
        queryset = DeviceInterface.objects.all()
        resource_name = 'deviceinterfaces'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        excludes = ['id']

    def dispatch_detail(self, request, **kwargs):
        interface_id = kwargs.pop('interface_id')
        del kwargs['interface_resource_name']

        kwargs['interface_id'] = interface_id

        return super(DeviceInterfacesResource, self).dispatch_detail(request, **kwargs)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        qs_filters = super(DeviceInterfacesResource, self).build_filters(filters)

        if 'device_id' in filters:
            qs_filters['device'] = filters['device_id']

        return qs_filters

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': DeviceResource._meta.resource_name,
            'interface_resource_name': InterfaceResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['device_id'] = bundle_or_obj.obj.device.id
            kwargs['interface_id'] = bundle_or_obj.obj.interface.id
        else:
            kwargs['device_id'] = bundle_or_obj.device.id
            kwargs['interface_id'] = bundle_or_obj.interface.id

        if DeviceResource._meta.api_name is not None:
            kwargs['api_name'] = DeviceResource._meta.api_name

        return self._build_reverse_url('api_dispatch_detail_device_interfaces',
                                       kwargs=kwargs)


class DeviceStateValueResource(ModelResource):
    device = fields.ToOneField(DeviceResource, 'device')
    method = fields.ToOneField(MethodResource, 'method')

    class Meta:
        queryset = StateValue.objects.all()
        resource_name = 'states'
        serializer = CamelCaseJSONSerializer()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch', 'delete']
        excludes = ['id']

    def dispatch_detail(self, request, **kwargs):
        method_id = kwargs.pop('method_id')
        del kwargs['state_resource_name']

        kwargs['method_id'] = method_id

        return super(DeviceStateValueResource, self).dispatch_detail(request, **kwargs)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        qs_filters = super(DeviceStateValueResource, self).build_filters(filters)

        if 'device_id' in filters:
            qs_filters['device'] = filters['device_id']

        return qs_filters

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': DeviceResource._meta.resource_name,
            'state_resource_name': DeviceStateValueResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['device_id'] = bundle_or_obj.obj.device.id
            kwargs['method_id'] = bundle_or_obj.obj.method.id
        else:
            kwargs['device_id'] = bundle_or_obj.device.id
            kwargs['method_id'] = bundle_or_obj.method.id

        if DeviceResource._meta.api_name is not None:
            kwargs['api_name'] = DeviceResource._meta.api_name

        return self._build_reverse_url('api_dispatch_detail_device_states',
                                       kwargs=kwargs)
