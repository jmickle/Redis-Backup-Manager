import redis
import logging
import os
import sys
import time
import datetime
import boto
import glob
import shutil
import s3tools
import socket
import json

class Backup:
        
    def __init__(self, sensuconf, server_name, port, save_directory, dbFileName, aws, prefix=None):
        self.server_name = server_name
        self.port = port
        self.save_directory = save_directory
        self.prefix = prefix
        self.rconn = redis.StrictRedis(host=self.server_name, port=self.port)
        self.dbFileName = dbFileName
        self.aws = aws
        self.sensuconf = sensuconf

    def run(self):
        if self.checkRunningSave() == True:
            logging.info('BGSave currently running, wont start another....')
            lastSave = self.rconn.lastsave()
        else:
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
                    self.alertSensu("Last Save time error!", self.server_name)
                    logging.error("Last save time error")
                    break
        
    def checkRunningSave(self):
        info = self.rconn.info()
        if info['redis_version'] >= '2.6':
            if info['rdb_bgsave_in_progress'] == 1:
                return True
            else:
                return False
        else:
            if info['bgsave_in_progress'] == 1:
                return True
            else:
                return False

    def saveFile(self):
        d = datetime.datetime.now()
        now = d.strftime("%Y%m%d%H%M")
        newSaveDir = os.path.join(self.save_directory, now)
        
        if self.prefix is not None:
            newFileName = self.prefix + "-" + now + ".rdb"
            logging.debug("New file name is %s" % newFileName)
        else:
            newFileName = self.server_name + "-" + now + ".rdb"
            logging.debug("New file name is %s" % newFileName)
        
        try:            
            os.chdir(self.save_directory)
            logging.debug("Creating directory: %s" % newSaveDir)
            os.mkdir(newSaveDir)
            logging.debug("Moving %s to file: %s" % (self.dbFileName, os.path.join(newSaveDir, newFileName)))
            shutil.copy2(self.dbFileName, os.path.join(newSaveDir, newFileName))
            logging.debug("Archiving...")
            source_file = os.path.join(newSaveDir, newFileName)
            keyname = self.server_name +"/" + newFileName
            #self.archiveArtifact(newSaveDir, newFileName)
            s3tools.upload(self.aws['s3_bucket'], self.aws['aws_access_key'], self.aws['aws_secret_key'], source_file, keyname)
            shutil.rmtree(newSaveDir)
        except:
            logging.error("Error encountered during file operations!\n %s")
            self.alertSensu("Redis File Operations Failed!", self.server_name)
            sys.exit(1)
            self.__archiveArtifact()
        
    def alertSensu(message, server_name):
        alert = {"name":server_name,"type":"check","output": message,"status":2,"handler":"pagerduty"}
        UDP_IP = self.sensuconf['sensu_agent_host']
        UDP_PORT = self.sensuconf['sensu_agent_port']
        sock - socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(alert), (UDP_IP,UDP_PORT))

        