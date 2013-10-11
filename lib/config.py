import configparser

class Config:
    
    def __init__(self, configFile):
        self.configFile = configFile
        self.conf = configparser.ConfigParser()
        self.conf.read(self.configFile)
        
        
    def getServers(self):
        for key, value in self.conf.items('default'):
            if key == "servers":
                servers = value.split(',')
                return servers
        
    def getSectionDetails(self, section):
        sectionDetails = {}
        options = self.conf.options(section)
        for option in options:
            try:
                sectionDetails[option] = self.conf.get(section,option)
            except:
                sectionDetails[option] = None
        return sectionDetails
    
    
# config = configparser.configparser()
# config.read("../config.ini")
# 
# config