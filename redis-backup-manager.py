#!/usr/bin/env python

import sys, time, os
import logging
from lib.daemon import daemon
from lib.redis import Backup
from lib.config import Config

# logger = logging.getLogger('Redis-Backups')
# logger.setLevel(logging.DEBUG)
# fh = logging.FileHandler('log/outapp.log')
# fh.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# logger.addHandler(fh)
# logger.addHandler(ch)

class BackupDaemon(daemon):
    
    
    def run(self):
        logging.info("---------- Redis Backups Starting ----------")
        configfile = os.path.join(os.environ['STARTPATH'], "config.ini")
        logging.debug("PATH IS %s" % configfile)
        conf = Config(os.path.join(os.environ['STARTPATH'], "/config.ini"))
        
        
        serverList = conf.getServers()
        logging.debug("got server list: %s" % serverList)
        
        servers = {}
        for server in serverList:
            servers[server] = conf.getSectionDetails(server)
        
        logging.info(servers)
        
        while True:
            time.sleep(1)
            #test = Backup(server_name="localhost", port=6379)
            #test.backup()
            
if __name__ == "__main__":
        logging.basicConfig(filename='log/outapp.log', level=logging.DEBUG)
        daemon = BackupDaemon("/Users/jonathanmickle/Documents/workspace/redis-backup-manager/test.pid")
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print("Unknown command")
                        sys.exit(2)
                sys.exit(0)
        else:
                print("usage: %s start|stop|restart") % sys.argv[0]
                sys.exit(2)
