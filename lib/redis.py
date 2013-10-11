import redis
import logging
import os
import sys
import time
import datetime

class Backup:
        
    def __init__(self, server_name, port, save_directory=None, prefix=None, dbFileName=None):
        self.server_name = server_name
        self.port = port
        self.save_directory = save_directory
        self.prefix = prefix
        self.rconn = redis.StrictRedis(host=self.server_name, port=self.port)
        self.dbFileName = dbFileName
    
    def run(self):
        if self.checkRunningSave() == False:
            logging.debug("no backup running")
            lastSave = self.rconn.lastsave()
            self.rconn.bgsave()
            
            while True:
                if self.checkRunningSave() == True:
                    logging.debug("BGSave still running.")
                    time.sleep(10)
                else:
                    tmpLastSave = self.rconn.lastsave()
                    if lastSave < tmpLastSave:
                        self.saveFile()
                        break
                    else:
                        logging.error("Last save time error")
                        break
            
        else:
            logging.info("RDB Save already processing.")
        
    def checkRunningSave(self):
        info = self.rconn.info()
        if info['rdb_bgsave_in_progress'] == 1:
            return True
        else:
            return False

    def saveFile(self):
        d = datetime.datetime.now()
        
        if self.prefix is not None:
            newFileName = self.prefix + "-" + d.strftime("%Y%m%d%H%M") + ".rdb"
        else:
            newFileName = self.server_name + "-" + d.strftime("%Y%m%d%H%M") + ".rdb"
        
        try:            
            os.chdir(self.save_directory)
            os.rename(self.dbFileName, newFileName)
        except:
            logging.error("Error encountered during file operations!\n %s")
            sys.exit(1)
            self.__archiveArtifact()
        
        
    def __archiveArtifact(self):
        pass
        





        