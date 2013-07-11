from haystack.indexes import *
from haystack import site
from models import Device, Interface


class DeviceIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    macAddress = CharField(model_attr='mac_address')
    owner = CharField(model_attr='owner__username')
    date_created = DateTimeField(model_attr='created_at')
    name = CharField(model_attr='name')

#    def index_queryset(self):
#        """Used when the entire index for model is updated."""
#        return Note.objects.filter(pub_date__lte=datetime.datetime.now())


class InterfaceIndex(SearchIndex):
    text = CharField(model_attr='name', document=True)

site.register(Device, DeviceIndex)
site.register(Interface, InterfaceIndex)
