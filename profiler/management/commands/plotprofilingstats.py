from django.core.management.base import NoArgsCommand, CommandError
from profiler.db import ProfilerDatabase
from profiler.plotter import StatsPlotter
import time

class Command(NoArgsCommand):
    help = 'Creates graphs based on profiling statistics.'
    can_import_settings = True
    
    def handle_noargs(self, **options):
        db = ProfilerDatabase()
        profiler_group_runs = db.get_profiler_group_runs()
        
        prompt_str = 'Which profiler run do you want to plot?\n'
        for index, profiler_group__run in enumerate(profiler_group_runs):
            prompt_str += '(%i) %s - (started: %s)\n' % (index, profiler_group__run['name'], profiler_group__run['started'])
        prompt_str += '\nType your choice: '
        profiler_group_run_index = int(raw_input(prompt_str))
        profiler_group_run = profiler_group_runs[profiler_group_run_index]
        
        try:
            start_time = time.time()
            dir_name = '%s_%s' % (profiler_group_run['name'], profiler_group_run['started'])
            plotter = StatsPlotter()
            plotter.plot(profiler_group_run['id'], dir_name)
        except KeyboardInterrupt:
            plotter.stop()
            self.stdout.write('\nPlotting stopped.\n')
        except Exception, e:
            raise CommandError(e)
        else:
            elapsed = time.time() - start_time
            self.stdout.write('Plotting finished in %i seconds\n' % elapsed)