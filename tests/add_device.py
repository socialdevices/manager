import json
import urllib2
import time

mac_address = "ab:bb:cc:dd:ee:ff"
interface_name = "talkingPhone"
methods = [{"name": "isWillingToTalk"}, {"name": "isSilence"}]

# Add device
url = 'http://localhost:8000/api/v1/device/'
headers = {'Content-Type': 'application/json'}
data = json.dumps({"mac_address": mac_address, "name": "Test device"})

request = urllib2.Request(url, data, headers)

try:
    response = urllib2.urlopen(request)
except urllib2.HTTPError, e:
    print 'The device could not be added.'
    print 'Error code:', e.code
else:
    print 'Device was added successfully! (HTTP ' + str(response.getcode()) + ')'


# Add interface
url = 'http://localhost:8000/api/v1/interface/'
headers = {'Content-Type': 'application/json'}
data = json.dumps({"name": interface_name, "methods": methods})

request = urllib2.Request(url, data, headers)

try:
    response = urllib2.urlopen(request)
except urllib2.HTTPError, e:
    print 'The interface could not be added.'
    print 'Error code:', e.code
else:
    print 'Interface was added successfully! (HTTP ' + str(response.getcode()) + ')'


# Add interface method
#url = 'http://localhost:8000/api/v1/interface/' + interface_name + '/'
#headers = {'Content-Type': 'application/json'}
#data = json.dumps({"methods": [{"name": "isWilling4"}]})

#request = urllib2.Request(url, data, headers)
#print url
#try:
#    response = urllib2.urlopen(request)
#except urllib2.HTTPError, e:
#    print 'The server couln\'t fulfill the request.'
#    print 'Error code:', e.code
#else:
#    print 'Method was added successfully for interface ' + interface_name + '! (HTTP ' + str(response.getcode()) + ')'
    
# Add interface for device
url = 'http://localhost:8000/api/v1/device/' + mac_address + '/'
headers = {'Content-Type': 'application/json'}
data = json.dumps({"interfaces": [{"name": interface_name}]})

request = urllib2.Request(url, data, headers)
request.get_method = lambda: 'PUT'

try:
    response = urllib2.urlopen(request)
except urllib2.HTTPError, e:
    print 'The interface could not be added for the device.'
    print 'Error code:', e.code
else:
    print 'Interface was added successfully for device! (HTTP ' + str(response.getcode()) + ')'
    
    
# Add state value for device
url = 'http://localhost:8000/api/v1/state_value/'
headers = {'Content-Type': 'application/json'}
data = json.dumps({"mac_address": mac_address, "interface_name": interface_name, "method_name": "isSilence", "value": "False"})

request = urllib2.Request(url, data, headers)

try:
    response = urllib2.urlopen(request)
except urllib2.HTTPError, e:
    print 'The state value could not be added.'
    print 'Error code:', e.code
else:
    print 'State value was added successfully! (HTTP ' + str(response.getcode()) + ')'


#time.sleep(1)

# Update state value for device
url = 'http://localhost:8000/api/v1/state_value/' + mac_address + '/' + interface_name + '/isSilence/'
headers = {'Content-Type': 'application/json'}
data = json.dumps({"value": "True"})

request = urllib2.Request(url, data, headers)
request.get_method = lambda: 'PUT'

try:
    response = urllib2.urlopen(request)
except urllib2.HTTPError, e:
    print 'The state value could not be updated.'
    print 'Error code:', e.code
else:
    print 'State value was updated successfully! (HTTP ' + str(response.getcode()) + ')'
