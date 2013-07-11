from core.models import Device, Interface, DeviceInterface, Method, StateValue, \
    MethodParameter
from tastypie.validation import Validation
import re

class DeviceResourceValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Missing data'}
        
        errors = {}
        
        # Check that all the required fields are provided
        if request.method == 'POST' and 'mac_address' not in bundle.data:
            errors['mac_address'] = 'Mac address is a required field'
        elif request.method == 'PUT' and 'mac_address' in bundle.data:
            errors['mac_address'] = 'Mac address cannot be updated'
            
        if request.method == 'POST' and 'name' not in bundle.data:
            errors['name'] = 'Device name is a required field'
        
        if request.method == 'PUT' and 'created_at' in bundle.data:
            errors['created_at'] = 'Created at cannot be updated'
        
        if request.method == 'PUT' and 'updated_at' in bundle.data:
            errors['updated_at'] = 'Updated at cannot be updated'
       
        if len(errors) == 0:
            mac_address = bundle.data.get('mac_address', None)
            name = bundle.data.get('name', None)
            
            # Check that a device with the mac address does not already exist
            if mac_address is not None and Device.objects.filter(mac_address=mac_address).exists():
                errors['mac_address'] = 'Duplicate mac address. Mac address %s already exists.' % mac_address
            
            # Validate mac address
            if mac_address is not None and not re.match(r'^(?:[0-9a-fA-F]{2}[:-]){5}(?:[0-9a-fA-F]){2}$', mac_address):
                errors['mac_address'] = 'Mac address format is incorrect'
            
            # Validate device name
            if name is not None and len(name) == 0:
                errors['name'] = 'Device name cannot be an empty string'
                        
        return errors



class DeviceInterfaceResourceValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Missing data'}
        
        errors = {}
        
        # Check that all the required fields are provided
        if request.method == 'POST' and 'interface_name' not in bundle.data:
            errors['interface_name'] = 'Interface name is a required field'
       
        if len(errors) == 0:
            interface_name = bundle.data.get('interface_name', None)
            mac_address = bundle.data.get('mac_address', None)
            
            # Check that the interface exists
            if interface_name is not None and not Interface.objects.filter(name=interface_name).exists():
                errors['interface_name'] = 'Interface %s does not exist.' % (interface_name)
            
            # Check that a device with the mac address does not already exist
            if interface_name is not None and mac_address is not None and DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists():
                errors['interface_name'] = 'Duplicate interface. Device %s already has interface %s.' % (mac_address, interface_name)
            
            # Validate interface name
            if interface_name is not None and len(interface_name) == 0:
                errors['interface_name'] = 'Interface name cannot be an empty string'
                        
        return errors



class DeviceStateValueResourceValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Missing data'}
        
        errors = {}
        
        # Check that all the required fields are provided
        if request.method == 'POST' and 'method_name' not in bundle.data:
            errors['method_name'] = 'Method name is a required field'
        
        if request.method == 'POST' and 'value' not in bundle.data:
            errors['value'] = 'Value is a required field'
       
        if request.method == 'PUT' and 'method_name' in bundle.data:
            errors['method_name'] = 'Method name cannot be updated'
       
        if request.method == 'PUT' and 'created_at' in bundle.data:
            errors['created_at'] = 'Created at cannot be updated'
        
        if request.method == 'PUT' and 'updated_at' in bundle.data:
            errors['updated_at'] = 'Updated at cannot be updated'
       
        if len(errors) == 0:
            arguments = bundle.data.get('arguments', {})
            value = bundle.data.get('value', None)
            method_name = bundle.data.get('method_name', None)
            interface_name = bundle.data.get('interface_name', None)
            mac_address = bundle.data.get('mac_address', None)
            
            # Check that the method exists
            if method_name is not None and not Method.objects.filter(name=method_name).exists():
                errors['method_name'] = 'Method %s does not exist.' % method_name
            
            # We only check if the interface exists for the device in case the device and interface already exist.
            # If the device or the interface does not exist, we want to return 404 Not Found instead of 400 Bad Request.
            if mac_address is not None and Device.objects.filter(mac_address=mac_address).exists() and Interface.objects.filter(name=interface_name).exists():
                # Check that the device has the interface
                if interface_name is not None and mac_address is not None and not DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists():
                    errors['method_name'] = 'Device %s does not have the appropriate interface for being able to store a state value for method %s.' % (mac_address, method_name)
            
            # Check that a method does not already exist
            if interface_name is not None and mac_address is not None and method_name is not None and StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists():
                errors['method_name'] = 'Duplicate method. Device %s has already added a value for method %s in interface %s.' % (mac_address, method_name, interface_name)
            
            # Validate method name
            if method_name is not None and len(method_name) == 0:
                errors['method_name'] = 'Method name cannot be an empty string'
            
            # Validate value
#            if value is not None and len(value) == 0:
#                errors['value'] = 'Value cannot be an empty string'
            
            # Validate arguments
            if request.method == 'PUT':
                m = re.search('/interface/(?P<interface_name>[\w]+)/method/(?P<method_name>[\w]+)/$', request.path_info)
                interface = m.group('interface_name')
                method = m.group('method_name')
            else:
                interface = interface_name
                method = method_name
            argument_error_list = []
            parameter_names = []
            method_parameters = MethodParameter.objects.filter(method__interface__name=interface, method__name=method)
            
            for parameter in method_parameters:
                parameter_names.append(parameter.name)
                if not parameter.name in arguments:
                    argument_error_list.append('%s is missing from arguments.' % parameter.name)
            
            for name in arguments.keys():
                if not name in parameter_names:
                    argument_error_list.append('Method %s does not accept %s as an argument.' % (method, name))
            
            if len(argument_error_list) > 0:
                errors['arguments'] = ' '.join(argument_error_list)
            
        return errors
