from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from proximity.listen import MyServer, MyTCPHandler
import socket
import sys

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--port',
                        '-p',
                        action='store',
                        type=int,
                        dest='port',
                        default=50007,
                        help='server port (default 50007)'),
            )
    help = "A server that stores proximity device information."
    can_import_settings = True
    
    def handle(self, *args, **options):
        HOST = "localhost"
    
        try:
            # Create the server
            server = MyServer((HOST, options.get('port')), MyTCPHandler, "localhost")
            self.stdout.write('Proximity server is running at %s:%s\n' % (HOST, options.get('port')))
            self.stdout.write('Quit the server with CONTROL-C.\n')
            
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
        except socket.error, e:
            raise CommandError(e.args[1])
        except KeyboardInterrupt:
            self.stdout.write('\nProximity server shutted down.\n')
            sys.exit(0)