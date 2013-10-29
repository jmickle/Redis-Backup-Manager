#!/usr/bin/env python

import sys, time, os
import logging
from lib.daemon import daemon
from lib.backup import Backup
from lib.config import Config

class BackupDaemon(daemon):
    
    
    def run(self):
        logging.info("---------- Redis Backups Starting ----------")
        configfile = os.path.join(os.environ['STARTPATH'], "config.ini")
        conf = Config(configfile)
        
        
        serverList = conf.getServers()
        logging.debug("got server list: %s" % serverList)
        
        servers = {}
        for server in serverList:
            servers[server] = conf.getSectionDetails(server)
        
        awsconf = conf.getSectionDetails("aws")
        
        logging.debug(servers)
        logging.debug(awsconf)
        
        
        while True:
            logging.debug("Backup process starting...")
            for server, value in servers.iteritems():
                logging.debug(value)
                if value['prefix'] == 'none':
                    prefix = None
                else:
                    prefix = value['prefix']
                job = Backup(server_name=value['hostname'], port=int(value['port']), save_directory=value['redis_save_dir'],
                             dbFileName=value['redis_db_name'],aws=awsconf,prefix=prefix)
                job.run()
                
            time.sleep(3600)

if __name__ == "__main__":
        logging.basicConfig(filename='log/app.log', level=logging.DEBUG)
        pidfile = os.getcwd() + "/proc.pid"
        daemon = BackupDaemon(pidfile)
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
                print("usage: %s start|stop|restart" % sys.argv[0]) 
                sys.exit(2)
