import urllib2
import urllib
import subprocess
import sys
import hashlib
import os.path

from decorators import *



class TalkingDevice(object):
    
    
    def __init__(self):
        pass
    
    
    """
    Synthesize speech with SSML markup, also wav-files can be embedded with <wave="filename">.
    Synthesis and wav-files reside on a server. Result is written to "filename".
    Available voices: david, william, allison, ransu.
    """
    @classmethod
    @body
    def say(self, params):

	print params
        try:
            text_encoded = urllib.quote_plus(params.get('str'), '')
            url_data = '?speaker=' + params.get('filter','david') + '&text=' + text_encoded
            url = 'http://131.228.164.158:8080/synth'
            full_url = url + url_data
        
            voices_dir = 'generated_voices/'
            filename = voices_dir + hashlib.sha1(full_url).hexdigest() + '.wav'
            
            if not os.path.isfile(filename):
                print "Getting wav from server.."
                if not os.path.exists(voices_dir):
                    os.makedirs(voices_dir)
                urllib.urlretrieve(full_url, filename)
    
            # on mac
            if sys.platform == 'darwin':
                sp = subprocess.Popen(["afplay", filename], executable="afplay")
    
            else:
                # on linux
                sp = subprocess.Popen(["aplay", filename], executable="aplay")    
    
            sp.wait()
        
        except Exception, e:
            print e
            raise e
        
        return

    @classmethod
    @body
    def play(self, soundFile):
        print(self.myDevice.getName() + ': play(' + soundFile + ')')

    @classmethod
    @precondition
    def isWilling(self):
	pass

    @classmethod
    @precondition
    def isSilent(self):
	pass
