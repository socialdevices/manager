# configuration reader for kurre sensory system
import ConfigParser, os

config = ConfigParser.ConfigParser()
try:
    pathname = os.path.abspath(__file__)
    config.readfp(open( pathname.replace( os.path.basename(pathname), '')  + '../conf/kics.cfg'))
except ConfigParser.ParsingError, e:
    print "error loading configuration for kurreSS: %s" % (e.message)
