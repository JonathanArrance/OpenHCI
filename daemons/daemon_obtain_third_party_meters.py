#!/usr/local/bin/python2.7

import sys
from transcirrus.common.daemon import Daemon
import transcirrus.operations.obtain_third_party_meters as third_party_ops

class MyDaemon(Daemon):
    def run(self):
        while True:
            third_party_ops.daemonize(True, 600)

if __name__ == "__main__":
    daemon = MyDaemon(sys.argv[1])
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