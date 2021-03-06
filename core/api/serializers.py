from django.core.serializers import json
from django.utils import simplejson
from tastypie.serializers import Serializer
import re


class CamelCaseJSONSerializer(Serializer):
    # This serializer also supports the formats that the default Serializer
    # class supports

    def to_json(self, data, options=None):
        # Changes underscore_separated names to camelCase names to go from
        # python convention to javacsript convention
        data = self.to_simple(data, options)

        def underscoreToCamel(match):
            return match.group()[0] + match.group()[2].upper()

        def camelize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z]_[a-z]", underscoreToCamel, key)
                    new_dict[new_key] = camelize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = camelize(data[i])
                return data
            return data

        camelized_data = camelize(data)

        return simplejson.dumps(camelized_data, cls=json.DjangoJSONEncoder,
                                sort_keys=True)

    def from_json(self, content):
        # Changes camelCase names to underscore_separated names to go from
        # javascript convention to python convention
        data = simplejson.loads(content)

        def camelToUnderscore(match):
            return match.group()[0] + "_" + match.group()[1].lower()

        def underscorize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z][A-Z]", camelToUnderscore, key)
                    new_dict[new_key] = underscorize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = underscorize(data[i])
                return data
            return data

        underscored_data = underscorize(data)

        return underscored_data
