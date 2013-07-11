from django.conf import settings
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from profiler.db import ProfilerDatabase
import logging
import multiprocessing
import os
import re

logger = logging.getLogger(__name__)

class StatsPlotter(object):
    
    def __init__(self):
        self.db = ProfilerDatabase()
        self.workers = []
    
    def plot(self, group_id, dir_name):
        functions = self.db.get_functions(group_id)
        profiler_group_run = self.db.get_profiler_group_run(group_id)
        x_label = profiler_group_run['x_label']
        num_profiler_runs = profiler_group_run['num_profiler_runs']
        
        tasks = multiprocessing.JoinableQueue()
        
        num_workers = multiprocessing.cpu_count() * 2
        
        # Start workers
        for i in xrange(num_workers):
            w = PlotWorker(tasks, dir_name, x_label, num_profiler_runs)
            self.workers.append(w)
            w.start()
        
        # Enqueue jobs
        for function in functions:
            data = {'id': function['id'], 'module': function['module'], 'name': function['name'], 'line': function['line']}
            tasks.put(data)
        
        # Add a poison pill for each worker
        for i in xrange(num_workers):
            tasks.put(None)
        
        # Wait for all the tasks to finish
        logger.debug('Waiting for worker processes')
        tasks.join()
    
    def stop(self):
        logger.debug('\nTerminating processes')
        for w in self.workers:
            w.terminate()
            w.join()
            logger.debug('%s terminated' % w.name)
            #print '%s.exitcode = %s' % (w.name, w.exitcode)
    

class PlotWorker(multiprocessing.Process):
    
    def __init__(self, queue, dir_name, x_label, num_profiler_runs):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.plot_dir = os.path.join(settings.PROFILER.get('PLOT_DIR', 'plots'), dir_name)
        self.x_label = x_label
        self.num_profiler_runs = num_profiler_runs
        #self.db = ProfilerDatabase()
    
    def run(self):
        db = ProfilerDatabase()
        logger.debug('Process %s started' % self.name)
        while True:
            function = self.queue.get()
            
            if function is not None:
                try:
                    function_stats = db.get_function_stats(function['id'])
                except Exception, e:
                    print str(e)
                else:
                    self._plot_function_stats(function, function_stats)
                    self.queue.task_done()
            # Poison pill means shutdown
            else:
                self.queue.task_done()
                break
        logger.debug('Process %s finished' % self.name)
        return
    
    def _plot_function_stats(self, function, function_stats):
        clean_module = re.sub('\W+', '_', function['module'])
        clean_name = re.sub('\W+', '_', function['name'])
        dir_name = os.path.join(self.plot_dir, '%s_%s_%s' % (clean_module, function['line'], clean_name))
        
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        stat_types = ['actual_calls', 'tottime', 'cumtime']
        
        for stat_type in stat_types:
            title = ''
            filename = ''
            if self.x_label == '':
                x_label = 'requests'
            else:
                x_label = self.x_label
            y_label = ''
            if stat_type == 'actual_calls':
                title = 'number of actual calls'
                filename = 'actual_calls'
                y_label = 'calls'
            elif stat_type == 'tottime':
                title = 'total time (excl. subfunctions)'
                filename = 'total_time_excl'
                y_label = 'time (s)'
            elif stat_type == 'cumtime':
                title = 'total time (incl. subfunctions)'
                filename = 'total_time_incl'
                y_label = 'time (s)'
                
#            values = {'x': [], 'y': []}
#            for stat in function_stats:
#                values['x'].append(stat['request_num'])
#                values['y'].append(stat[stat_type])
#            
#            figure_title = 'Cumulative %s\n %s:%s(%s)' % (title, function['module'], function['line'], function['name'])
#            figure_filename = os.path.join(dir_name, filename + '_cumulative' + '.png')
#            self._draw_figure(figure_title, figure_filename, values['x'], values['y'], x_label, y_label)
            
            
            values = {'x': [], 'y': []}
            #previous = 0
            for stat in function_stats:
                values['x'].append(stat['request_num'])
                values['y'].append(stat[stat_type])
                #values['y'].append(stat[stat_type] - previous)
                
                #previous = stat[stat_type]
            
            figure_title = '%s\n %s:%s(%s)\nAverage of %i runs' % (title, function['module'], function['line'], function['name'], self.num_profiler_runs)
            figure_filename = os.path.join(dir_name, filename + '.png')
            self._draw_figure(figure_title, figure_filename, values['x'], values['y'], x_label, y_label)
        
        #print cumulative_cumtime_values['request_num']
        #print cumulative_cumtime_values['cumtime']
    
    def _draw_figure(self, title, filename, x_values, y_values, x_label, y_label):
        figure = Figure()
        canvas = FigureCanvas(figure)
        axes = figure.add_axes([0.15, 0.1, 0.7, 0.7])
        axes.plot(x_values, y_values)
        axes.grid(True)
        axes.set_xlabel(x_label)
        axes.set_ylabel(y_label)
        axes.set_title(title)
        figure.set_figheight(8)
        figure.set_figwidth(15)
        try:
            figure.savefig(filename)
            #canvas.print_png(filename)
        except Exception, e:
            logger.error(title)
            logger.error(filename)
            logger.error(str(e))
        
#def plot_worker(kurre_plotter):
#    while True:
#        function = kurre_plotter.get_function()
#        kurre_plotter.

#def main():
#    parser = argparse.ArgumentParser(description="A utility for plotting the stats gotten with Kurre profiler")
#    parser.add_argument('-p', '--profiler', default=1, type=int, dest='profiler_run_id', help='the profiler run id')
#    args = parser.parse_args()
#
#    
#    try:
#        start_time = time.time()
#        plotter = StatsPlotter()
#        plotter.plot(args.profiler_run_id)
#        
#    except KeyboardInterrupt:
#        plotter.stop()
#        sys.stdout.write('\nPlotting shutted down.\n')
#        sys.exit(0)
#    except Exception, e:
#        print str(e)
#        sys.exit(1)
#    else:
#        elapsed = time.time() - start_time
#        print 'Plotting finished in %i seconds\n' % elapsed
#        sys.exit(0)
#    
#if __name__ == "__main__":
#    main()
