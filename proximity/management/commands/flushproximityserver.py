from core.clients import ProximityClient, ProximityClientConnectionError
from django.core.management.base import CommandError, NoArgsCommand

class Command(NoArgsCommand):
    help = "Flushes the proximity server."
    can_import_settings = True
    
    def handle_noargs(self, **options):
        client = ProximityClient()
        
        try:
            client.flush()
        except ProximityClientConnectionError, e:
            raise CommandError(e)
        else:
            self.stdout.write('Proximity server flushed.\n')