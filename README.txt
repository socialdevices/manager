Remember to start the proximity server. The proximity server can be started with the following management command:

python manage.py runproximityserver


Remember to start the memcached daemon. The memcached daemon can be started with the following command:

memcached -d -u USER -p 11211 -m 64


You can use the profiler app to profile Kurre. Profiling can be started with the following command:

python manage.py profile -n 100

, where n is the number of requests to profile. Deleting profiling stats is possible with the following command:

python manage.py profilerclear

Creating graphs based on the profiler stats is possible using the following command:

python manage.py plotprofilingstats
