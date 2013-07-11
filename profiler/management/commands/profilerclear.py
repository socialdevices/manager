from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option
import os

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
            make_option('--noinput',
                        action='store_false',
                        dest='interactive',
                        default=True,
                        help='Tells Django to NOT prompt the user for input of any kind.'),
            )
    help = 'Deletes the profiler sqlite database and removes all files in the profiler log directory.'
    can_import_settings = True
    
    def handle_noargs(self, **options):
        interactive = options.get('interactive')
        
        if interactive:
            confirm = raw_input("""You have requested to clear the profiler.
This will IRREVERSIBLY DESTROY all data currently associated with the profiler,
and return the state of the profiler to the state it was in before any profiling.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """)
        else:
            confirm = 'yes'
        
        if confirm == 'yes':
            log_dir = settings.PROFILER.get('LOG_DIR', None)
            
            if log_dir is not None:
                for filename in os.listdir(log_dir):
                    file_path = os.path.join(log_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception, e:
                        raise CommandError(e)
            else:
                raise CommandError('No log directory has been defined in the settings for the profiler.')
            
            db_dir = os.path.dirname(__file__).replace('management/commands', '')
            db_path = os.path.join(db_dir, 'profiler.sqlite')
            try:
                if os.path.isfile(db_path):
                    os.remove(db_path)
            except Exception, e:
                raise CommandError(e)
            
            self.stdout.write('Profiling data cleared successfully.\n')
        else:
            self.stdout.write('Clearing of the profiler cancelled.\n')