# configuration reader for kurre sensory system
import ConfigParser

config = ConfigParser.ConfigParser()
try:
    config.readfp(open('plugins/state/kurreSS.cfg'))
except ConfigParser.ParsingError, e:
    print "error loading configuration for kurreSS: %s" % (e.message)
