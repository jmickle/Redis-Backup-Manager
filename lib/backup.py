import redis
import logging
import os
import sys
import time
import datetime
import boto
import glob
import shutil

class Backup:
        
    def __init__(self, server_name, port, save_directory, dbFileName, aws, prefix=None):
        self.server_name = server_name
        self.port = port
        self.save_directory = save_directory
        self.prefix = prefix
        self.rconn = redis.StrictRedis(host=self.server_name, port=self.port)
        self.dbFileName = dbFileName
        self.aws = aws
    
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
            os.rename(self.dbFileName, os.path.join(newSaveDir, newFileName))
            logging.debug("Archiving...")
            self.archiveArtifact(newSaveDir, newFileName)
        except:
            logging.error("Error encountered during file operations!\n %s")
            sys.exit(1)
            self.__archiveArtifact()
        
        
    def archiveArtifact(self, dir, artifact):
        os.chdir(dir)
        try:
            os.system("split -b500m " + artifact + " backup.")
        except:
            logging.error("Error splitting file!")
            sys.exit(2)
        
        files = glob.glob("backup.*")
        logging.debug("got files %s" % files)
        
        conn = boto.connect_s3(aws_access_key_id=self.aws['aws_access_key'], aws_secret_access_key=self.aws['aws_secret_key'])
        bucket = conn.lookup(self.aws['s3_bucket'])
        
        mp = bucket.initiate_multipart_upload(self.server_name +"/" + artifact)

        i = 0
        filenum = 1
        while i < len(files):
            logging.debug("Trying to upload %s" % files[i])
            fp = open(files[i], 'rb')
            mp.upload_part_from_file(fp, filenum)
            fp.close()
            
            i += 1
            filenum += 1
            
        for part in mp:
            logging.debug(part)
        
        logging.debug("Upload complete")
        mp.complete_upload()
        
        #Delete backups to not fill up disk space
        os.chdir("../")
        shutil.rmtree(dir)

        