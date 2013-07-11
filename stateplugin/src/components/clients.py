import json
import requests
import netifaces

class KurreClient():
    
    def __init__(self):
        self.kurre = 'http://kurre.soberit.hut.fi'
        self.apipath = '/api/v3'
        
        # get own device id
        
        
        # save to conf

        
        # mark self as online
    
    def _get_self_id(self):
        id_candidates = [j['addr'] for i in netifaces.interfaces() for j in netifaces.ifaddresses(i)[n.AF_LINK] if j['addr']]
        limit = '1'
        
        url = ''

    def _send_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
        except requests.ConnectionError:
            raise KurreConnectionError('The connection to kurre at %s failed' % url)
        except requests.Timeout:
            raise KurreTimeoutError('The request to kurre at %s timed out' % url)
        else:
            if response.status_code == 404:
                raise KurreNotFoundError('Url %s not found for kurre' % url)
            return response
            


class KurreError(Exception):
    """Base class for Kurre client errors."""
    pass


class KurreConnectionError(KurreError):
    """Used to indicate that a connection to kurre failed."""
    pass


class KurreTimeoutError(KurreError):
    """Used to indicate that a connection to kurre timed out."""
    pass


class KurreNotFoundError(KurreError):
    """Used to indicate that a HTTP 404 Not Found was received."""
    pass


class KurreInternalServerError(KurreError):
    """Used to indicate that a HTTP 500 Internal Server Error was received."""
    pass
    
class KurreReplyParseError(KurreError):
    """Used to indicate that kurre reply could not be parsed."""
    pass
