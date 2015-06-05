#!/bin/bash
# ceilometer_memory_patch daemon
# chkconfig: 345 20 80
# description: ceilometer_memory_patch daemon
# processname: ceilometer_memory_patch

PATH=/bin:/usr/bin:/sbin:/usr/sbin
DAEMON=/usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch.sh
NAME=ceilometer_memory_patch
PIDFILE=/var/run/$NAME.pid
#SCRIPTNAME=/etc/init.d/$NAME

test -e $DAEMON || exit 0

. /lib/lsb/init-functions

case "$1" in
  start)
     log_success_msg "Starting Zero Connect Server"
     /usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/daemons/daemon_obtain_memory_usage.py $PIDFILE start
#     start_daemon -p $PIDFILE $DAEMON
#     PID=`ps x |grep '/usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/core/ciac_server.py' | head -1 | awk '{print $1}'`
#     echo $PID > $PIDFILE
   ;;
  stop)
     log_success_msg "Stopping Zero Connect Server"
     /usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/daemons/daemon_obtain_memory_usage.py $PIDFILE stop
#     killproc -p $PIDFILE $DAEMON
#     PID=`ps x |grep '/usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/core/ciac_server.py' | head -1 | awk '{print $1}'`
#     kill -9 $PID
#     log_success_msg $PID
   ;;
  force-reload|restart)
     $0 stop
     $0 start
   ;;
#  status)
#     PID=`ps x |grep '/usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/core/ciac_server.py' | head -1 | awk '{print $1}'`
#     if [[ `pidof -x /usr/local/bin/python2.7 ciac_server.py` -eq $PID ]]; then
#         echo 'Zero Connect Server is running' $PID
#     else
#         if [[ `pidof -x /usr/local/bin/python2.7 ciac_server.py` -ne $PID ]]; then
#             echo 'Zero Connect Server is dead'
#         fi
#     fi
#   ;;
 *)
   echo "Usage: /etc/init.d/zero_connect {start|stop|restart|force-reload}"
   exit 1
  ;;
esac

exit 0