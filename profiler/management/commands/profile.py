from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from profiler.backends import get_backend_class
from profiler.eventhandler import EventHandler
import pyinotify
import threading
import time

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--num',
                        '-n',
                        action='store',
                        type=int,
                        dest='num',
                        default=100,
                        help='number of profiling calls (default 100)'),
            make_option('--runs',
                        '-r',
                        action='store',
                        type=int,
                        dest='runs',
                        default=1,
                        help='number of profile runs (default 1)'),
            make_option('--first',
                        '-f',
                        action='store',
                        type=int,
                        dest='first',
                        default=1,
                        help='the index of the call from where to start profiling (default 1)'),
            make_option('--increment',
                        '-i',
                        action='store',
                        type=int,
                        dest='increment',
                        default=1,
                        help='the profiling call increment (default 1)'),
            )
    help = "A profiler for testing Kurre's performance."
    can_import_settings = True
    
    def handle(self, *args, **options):
        if getattr(settings, 'PROFILING', False):
            try:
                wm = pyinotify.WatchManager() # Watch Manager
                mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY # watched events
                
                condition = threading.Condition()
                notifier = pyinotify.ThreadedNotifier(wm, EventHandler(condition))
                notifier.start()
                
                watch_path = settings.PROFILER.get('LOG_DIR', '')
                wdd = wm.add_watch(watch_path, mask)
            except Exception, e:
                raise CommandError(e)
            else:
                backend_class = get_backend_class(settings.PROFILER.get('BACKEND', 'profiler.backends.kurre.KurreProfiler'))
                profiler = backend_class(options.get('runs'), options.get('first'), options.get('num'), options.get('increment'), condition)
                
                profiler_tests = profiler.get_tests()
                
                prompt_str = 'Which profiler test do you want to run?\n'
                for index, profiler_test in enumerate(profiler_tests):
                    prompt_str += '(%i) %s\n' % (index, profiler_test)
                prompt_str += '\nType your choice: '
                test_index = int(raw_input(prompt_str))
                
                try:
                    self.stdout.write('Starting profiling\n')
                    start_time = time.time()
                    profiler.start_profiling(test_index)
                except Exception, e:
                    raise CommandError(e)
                else:
                    elapsed = time.time() - start_time
                    self.stdout.write('Profiling finished in %i seconds\n' % elapsed)
            finally:
                wm.rm_watch(wdd.values())
                notifier.stop()
        else:
            raise CommandError('Profiling is turned off in the settings.')