#!/usr/bin/python2.7
import sys
from transcirrus.common.daemon import Daemon
import transcirrus.rest.app as api

server = None

class RestAPIDaemon(Daemon):
    def run(self):
        api.launch()

if __name__ == "__main__":
    daemon = RestAPIDaemon(sys.argv[1])
    if len(sys.argv) == 3:
        if 'start' == sys.argv[2]:
            daemon.start()
        elif 'stop' == sys.argv[2]:
            daemon.stop()
        elif 'restart' == sys.argv[2]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)