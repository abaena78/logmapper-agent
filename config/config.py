# -*- coding: utf-8 -*-

# XXXXXX.py : part of LogMapper
# 
# Copyright (c) 2018, Jorge Andres Baena abaena78@gmail.com
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
===============================================================================
Configuration defintions for Logmapper

@author: abaena
===============================================================================
"""

import os
import configparser

#==============================================================================
# Constants definitions
#==============================================================================

__version__ = "0.0.4"

CONFIGFILE_NAME = "conf.ini"

DBFILE_SUFIX_BASEDB = '_base'
DBFILE_SUFIX_EVENTSDB = '_events'
DBFILE_SUFIX_DATADB = '_lmdata'
DBFILE_SUFIX_MONDB = '_mon'

SOCKET_SERVER_THREAD_KEY="ThreadSocketServer"
THREAD_PREFIX = 'LMP_'
THREAD_MONITOR=THREAD_PREFIX+'MON_'
THREAD_READER=THREAD_PREFIX+'READER_'
THREAD_MAPPER=THREAD_PREFIX+'MAPPER_'
THREAD_SAVEDB=THREAD_PREFIX+'SAVEDB'

MONITOR_TYPE_HOST = "host"
MONITOR_TYPE_SPRINGMICROSERVICE = "spring_microservice"
MONITOR_TYPE_TOMCAT = "tomcat"
MONITOR_TYPE_POSTGRES = "postgres"

#==============================================================================
# Properties keys
#==============================================================================


SECTION_LOGMAPPER = "LOGMAPPER"
PROP_DIR_BASE = "dirbase"
PROP_DIR_LOG = "dirlog"
PROP_DIR_DATA = "dirdata"
PROP_LOGFILENAME = "logger.file"
PROP_DEBUGLEVEL = "logger.debug.level"
PROP_AGENTKEY = "agent.key"
PROP_AGENTIP = "agent.ip"
PROP_AGENTPORT = "agent.port" 
PROP_MASTERIP = "master.ip"
PROP_MASTERPORT = "master.port"
PROP_ENABLESENDDATA = "master.senddata.enable"
PROP_TESTMODE = "agent.test.mode"

SECTION_GENERAL = "GENERAL"
PROP_HOSTNAME = "hostname"

SECTION_READERS_LIST = "READERS_LIST"
PROP_READERSENABLE = "readers.enable"
PROP_READERS_LIST = "readers.list"

SECTION_READER = 'READER_'
PROP_READER_KEY = "reader.key"
PROP_READER_ENABLE = "reader.enable"
PROP_READER_COMPONENT = "reader.component"
PROP_READER_SOURCEFILEPATH = "reader.sourcefilepath"
PROP_READER_MODULENAME = "reader.parser.moduleName"
PROP_READER_CLASSNAME = "reader.parser.className"

SECTION_MONITORS_LIST = "COMPONENT_MONITORS_LIST"
PROP_MONITORS_ENABLE = "monitors.enable"
PROP_MONITORS_LIST = "monitors.list"

SECTION_MONITOR = 'MONITOR_'
PROP_MON_KEY = "monitor.key"
PROP_MON_ENABLE = "monitor.enable"
PROP_MON_COMPONENT_LIST = "monitor.component.list"
PROP_MON_TYPE = "monitor.type" #host,spring_microservice,tomcat,postgres
PROP_MON_INTERVAL = "monitor.interval"
PROP_MON_URL = "monitor.url"
PROP_MON_HOST = "monitor.host"
PROP_MON_PORT = "monitor.port"
PROP_MON_USER = "monitor.user"
PROP_MON_PWD = "monitor.password"



#==============================================================================
# Classes definitions
#==============================================================================

class LogMapperAgentConfig:
    
    def __init__(self):
        
        self.agentKey = None
        
        self.hostname = None 
              
        self.masterHost = None
        
        self.masterPort = None
        
        self.logFilePath = None
        
        self.logLevel = None
        
        
    def __str__(self):
        return "LogMapperAgentConfig:[" +"agentKey="+str(self.agentKey) +", hostname="+str(self.hostname)
        +", masterHost="+str(self.key) +", masterPort="+str(self.masterPort) + "]"
        

class ReaderConfig:
    
    def __init__(self):
        
        # Key or Unique code that identify the node
        self.key = None
        
        self.section = None
        
        self.enable = False
        
        self.component = None
        
        self.hostname = None         
        
        self.sourcefilepath = None
        
        self.moduleName = None
        
        self.className = None
        
        self.dbBasePath = None
        
        self.dbEventsPath = None
        
        self.dbDataPath = None
        
        self.masterHost = None
        
        self.masterPort = None
        
        self.enableSendData = None
        
    def __str__(self):
        return "ReaderConfig:[" +"sourcefilepath="+str(self.sourcefilepath) +", component="+str(self.component) + ", key="+str(self.key) +", hostname="+str(self.hostname) + "]"
      

class MonitorConfig:
    
    def __init__(self):
        
        # Key or Unique code that identify the node
        self.key = None
        
        self.section = None
        
        self.enable = False
        
        self.components = None
        
        self.hostname = None 
        
        self.type = None
        
        self.interval = None
        
        self.url = None
        
        self.host = None
        
        self.port = None
        
        self.user = None
        
        self.pwd = None
        
        self.dbMonitorPath = None
        
        self.masterHost = None
        
        self.masterPort = None
        
        self.enableSendData = None
        
    def __str__(self):
        return "ComponentMonitorConfig:[" +"component="+str(self.component) + ", key="+str(self.key) +", host="+str(self.host) +", port="+str(self.port) + "]"
     
#==============================================================================
# Functions
#==============================================================================  

def loadConfig(filepath=CONFIGFILE_NAME, resetconfig=False):
    """ 
    ===========================================================================
    Load configuration from file
    If the file not exist create a new one.
    ===========================================================================   
    
    **Args**:
        filepath: path of the file -- str       
    **Returns**:
        ConfigParser class. Query setting with: ``config.get(section, key)``   
    """    
    if not filepath:
       filepath=CONFIGFILE_NAME 
    
    # Check if there is already a configurtion file
    if not os.path.isfile(filepath):
        createDefaultConfigfile()
        
    if resetconfig:
        createDefaultConfigfile()
        
    config = configparser.ConfigParser()
    config.read(filepath)
    return config 


def printConfig(config):
    """ 
    ===========================================================================
    Print in logger config data
    ===========================================================================   
    
    **Args**:
        None        
    **Returns**:
        None  
    """
    for section in config.sections():
        for key in config[section]: 
            print(section+'.'+key+'='+config.get(section, key))
       

def saveConfig(config):
    """ 
    ===========================================================================
    Print in logger config data
    ===========================================================================   
    
    **Args**:
        None        
    **Returns**:
        None  
    """
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(CONFIGFILE_NAME, 'w')
    config.write(cfgfile)
    cfgfile.close()  
    

def getDbFilePath(config, key):
    """ 
    ===========================================================================
    Print in logger config data
    ===========================================================================   
    
    **Args**:
        * config
        * key        
    **Returns**:
        None  
    """
    dataDir = config.get(SECTION_LOGMAPPER, PROP_DIR_DATA)
    return dataDir + key + '.db'
    
def getReaders(config):
    """ 
    ===========================================================================
    Get list of readers
    ===========================================================================   
    
    **Args**:
        config: config object        
    **Returns**:
        List of readers -- [str]
    """    
    readers = config.get(SECTION_READERS_LIST, PROP_READERS_LIST) 
    readers = readers.split(',')
    return readers 

def loadLogMapperAgentConfig(config): 
    """ 
    ===========================================================================
    Copy data from config object into ReaderConfig class
    ===========================================================================   
    
    **Args**:
        * config: rey
        * readerName:  eryte    
    **Returns**:
        Object with configuration data -- config.ReaderConfig 
    """     
    logMapperAgentConfig = LogMapperAgentConfig()  
    logMapperAgentConfig.agentKey = config.get(SECTION_LOGMAPPER, PROP_AGENTKEY)
    logMapperAgentConfig.hostname = config.get(SECTION_GENERAL, PROP_HOSTNAME)
    logMapperAgentConfig.masterHost = config.get(SECTION_LOGMAPPER, PROP_MASTERIP)
    logMapperAgentConfig.masterPort = config.getint(SECTION_LOGMAPPER, PROP_MASTERPORT)
    logMapperAgentConfig.logFilePath = config.get(SECTION_LOGMAPPER, PROP_DIR_LOG)+config.get(SECTION_LOGMAPPER, PROP_LOGFILENAME)
    return logMapperAgentConfig
    
def loadReaderConfig(config, key):
    """ 
    ===========================================================================
    Copy data from config object into ReaderConfig class
    ===========================================================================   
    
    **Args**:
        * config: rey
        * readerName:  eryte    
    **Returns**:
        Object with configuration data -- config.ReaderConfig 
    """     
    readerConfig = ReaderConfig()
    readerConfig.section = SECTION_READER+key
    readerConfig.key =  config.get(readerConfig.section, PROP_READER_KEY)
    readerConfig.enable = config.getboolean(readerConfig.section, PROP_READER_ENABLE)
    readerConfig.hostname = config.get(SECTION_GENERAL, PROP_HOSTNAME)
    readerConfig.component = config.get(readerConfig.section, PROP_READER_COMPONENT)
    readerConfig.sourcefilepath = config.get(readerConfig.section, PROP_READER_SOURCEFILEPATH)
    readerConfig.moduleName = config.get(readerConfig.section, PROP_READER_MODULENAME)
    readerConfig.className = config.get(readerConfig.section, PROP_READER_CLASSNAME)
    
    readerConfig.dbBasePath = getDbFilePath(config, readerConfig.key+DBFILE_SUFIX_BASEDB)
    readerConfig.dbEventsPath = getDbFilePath(config, readerConfig.key+DBFILE_SUFIX_EVENTSDB)
    readerConfig.dbDataPath = getDbFilePath(config, readerConfig.key+DBFILE_SUFIX_DATADB) 
    
    readerConfig.masterHost = config.get(SECTION_LOGMAPPER, PROP_MASTERIP)        
    readerConfig.masterPort = config.getint(SECTION_LOGMAPPER, PROP_MASTERPORT)
    readerConfig.enableSendData = config.getboolean(SECTION_LOGMAPPER, PROP_ENABLESENDDATA)
    
    return readerConfig  
   

def getMonitors(config):
    """ 
    ===========================================================================
    Get list of readers
    ===========================================================================   
    
    **Args**:
        config: config object        
    **Returns**:
        List of readers -- [str]
    """    
    monitors = config.get(SECTION_MONITORS_LIST, PROP_MONITORS_LIST) 
    monitors = monitors.split(',')
    return monitors  

def loadMonitorConfig(config, key):
    """ 
    ===========================================================================
    Copy data from config object into ReaderConfig class
    ===========================================================================   
    
    **Args**:
        * config: 
        * key:      
    **Returns**:
        Object with configuration data -- config.ComponentMonitorConfig 
    """     
    monitorConfig = MonitorConfig()
    monitorConfig.section = SECTION_MONITOR+key 
    monitorConfig.key = config.get(monitorConfig.section, PROP_MON_KEY)
    monitorConfig.enable = config.getboolean(monitorConfig.section, PROP_MON_ENABLE)
    monitorConfig.hostname = config.get(SECTION_GENERAL, PROP_HOSTNAME)
    monitorConfig.components = config.get(monitorConfig.section, PROP_MON_COMPONENT_LIST)
    monitorConfig.type = config.get(monitorConfig.section, PROP_MON_TYPE)
    monitorConfig.interval = config.getfloat(monitorConfig.section, PROP_MON_INTERVAL)
    monitorConfig.url = config.get(monitorConfig.section, PROP_MON_URL)
    monitorConfig.host = config.get(monitorConfig.section, PROP_MON_HOST)
    monitorConfig.port = config.getint(monitorConfig.section, PROP_MON_PORT)
    monitorConfig.user = config.get(monitorConfig.section, PROP_MON_USER)
    monitorConfig.pwd = config.get(monitorConfig.section, PROP_MON_PWD) 
    
    monitorConfig.dbMonitorPath=getDbFilePath(config, key+DBFILE_SUFIX_MONDB)   
    
    monitorConfig.masterHost = config.get(SECTION_LOGMAPPER, PROP_MASTERIP)        
    monitorConfig.masterPort = config.getint(SECTION_LOGMAPPER, PROP_MASTERPORT)
    monitorConfig.enableSendData = config.getboolean(SECTION_LOGMAPPER, PROP_ENABLESENDDATA)
    
    return monitorConfig     
  

def createDefaultConfigfile():
    """ 
    ===========================================================================
    Create configfile with Default Data
    ===========================================================================   
    
    **Args**:
        None        
    **Returns**:
        None  
    """    
    # Add content to the file
    config = configparser.ConfigParser()
    config.add_section(SECTION_LOGMAPPER)
    config.set(SECTION_LOGMAPPER, PROP_DIR_BASE, "/logmapper/")
    config.set(SECTION_LOGMAPPER, PROP_DIR_LOG, "/logmapper/log/")
    config.set(SECTION_LOGMAPPER, PROP_DIR_DATA, "/logmapper/data/")
    config.set(SECTION_LOGMAPPER, PROP_LOGFILENAME, "logmapper-agent.log")
    config.set(SECTION_LOGMAPPER, PROP_DEBUGLEVEL, 'INFO')

    config.set(SECTION_LOGMAPPER, PROP_AGENTKEY, 'agent-1')
    config.set(SECTION_LOGMAPPER, PROP_AGENTIP, '127.0.0.1')
    config.set(SECTION_LOGMAPPER, PROP_AGENTPORT, '5001')
    config.set(SECTION_LOGMAPPER, PROP_MASTERIP, '127.0.0.1')
    config.set(SECTION_LOGMAPPER, PROP_MASTERPORT, '5005')
    config.set(SECTION_LOGMAPPER, PROP_ENABLESENDDATA, str(False))
    config.set(SECTION_LOGMAPPER, PROP_TESTMODE, str(True)) 
    

    config.add_section(SECTION_GENERAL)
    config.set(SECTION_GENERAL, PROP_HOSTNAME, 'localhost')
         
        
    config.add_section(SECTION_READERS_LIST)
    config.set(SECTION_READERS_LIST, PROP_READERSENABLE, str(True))
#    config.set(SECTION_READERS_LIST, PROP_READERS_LIST, 'device') 
#    config.set(SECTION_READERS_LIST, PROP_READERS_LIST, 'microserviceregister,security,alarm,web,parameter,audit,concurrent,device,devicetypetok,notification,transaction,directory,location,smentity') 
#    config.set(SECTION_READERS_LIST, PROP_READERS_LIST, 'microserviceregister,account,smsecurity,alarm,bpm,integrator,parameter,audit,concurrent,device,notification,transaction,directory,location,etl,evaluation,operationlog,reporttemplate,user,emailreceiver,healthcampaign,databuffer,powerdistribution,abt-trx,credito,credito-bpmprocess,smappmanager-web,smscada-web,previapp-web,smicetex-web,integrator-ws') 
    config.set(SECTION_READERS_LIST, PROP_READERS_LIST, 'microserviceregister,account,smsecurity,alarm,bpm,integrator,parameter,audit,concurrent,device,notification,transaction,directory,location,etl,evaluation,operationlog,reporttemplate,user,emailreceiver,databuffer,transfer,batchmanager,custommodel,devinterface-trx,custommodel-bpmprocess,smdemo-web') 
   
    
    section=SECTION_READER+'microserviceregister'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(False))  
    config.set(section, PROP_READER_KEY, 'microserviceregister')    
    config.set(section, PROP_READER_COMPONENT, 'microserviceregister')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/microserviceregister-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
    
    section=SECTION_READER+'account'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'account')
    config.set(section, PROP_READER_COMPONENT, 'account')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/account-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
    
    section=SECTION_READER+'smsecurity'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'smsecurity')
    config.set(section, PROP_READER_COMPONENT, 'smsecurity')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/smsecurity-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')    

    section=SECTION_READER+'alarm'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'alarm')      
    config.set(section, PROP_READER_COMPONENT, 'alarm')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/alarm-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
       
    section=SECTION_READER+'parameter'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True)) 
    config.set(section, PROP_READER_KEY, 'parameter')     
    config.set(section, PROP_READER_COMPONENT, 'parameter')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/parameter-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'audit'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True)) 
    config.set(section, PROP_READER_KEY, 'audit')     
    config.set(section, PROP_READER_COMPONENT, 'audit')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/audit-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
    
    section=SECTION_READER+'bpm'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True)) 
    config.set(section, PROP_READER_KEY, 'bpm')     
    config.set(section, PROP_READER_COMPONENT, 'bpm')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/bpm-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')    
    
    section=SECTION_READER+'concurrent'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True)) 
    config.set(section, PROP_READER_KEY, 'concurrent')     
    config.set(section, PROP_READER_COMPONENT, 'concurrent')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/concurrent-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'device'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True)) 
    config.set(section, PROP_READER_KEY, 'device')     
    config.set(section, PROP_READER_COMPONENT, 'device')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/device-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser') 

    section=SECTION_READER+'notification'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))  
    config.set(section, PROP_READER_KEY, 'notification')    
    config.set(section, PROP_READER_COMPONENT, 'notification')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/notification-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
    
    section=SECTION_READER+'transaction'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'transaction')      
    config.set(section, PROP_READER_COMPONENT, 'transaction')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/transaction-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')   
    
    section=SECTION_READER+'directory'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'directory')      
    config.set(section, PROP_READER_COMPONENT, 'directory')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/directory-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')  

    section=SECTION_READER+'location'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))  
    config.set(section, PROP_READER_KEY, 'location')    
    config.set(section, PROP_READER_COMPONENT, 'location')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/location-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser') 
    
    section=SECTION_READER+'etl'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'etl')
    config.set(section, PROP_READER_COMPONENT, 'etl')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/etl-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'evaluation'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'evaluation')
    config.set(section, PROP_READER_COMPONENT, 'evaluation')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/evaluation-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'integrator'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'integrator')
    config.set(section, PROP_READER_COMPONENT, 'integrator')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/integrator-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'operationlog'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'operationlog')
    config.set(section, PROP_READER_COMPONENT, 'operationlog')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/operationlog-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'reporttemplate'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'reporttemplate')
    config.set(section, PROP_READER_COMPONENT, 'reporttemplate')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/reporttemplate-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'user'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'user')
    config.set(section, PROP_READER_COMPONENT, 'user')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/user-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'emailreceiver'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'emailreceiver')
    config.set(section, PROP_READER_COMPONENT, 'emailreceiver')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/emailreceiver-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'healthcampaign'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'healthcampaign')
    config.set(section, PROP_READER_COMPONENT, 'healthcampaign')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/healthcampaign-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'databuffer'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'databuffer')
    config.set(section, PROP_READER_COMPONENT, 'databuffer')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/databuffer-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'powerdistribution'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'powerdistribution')
    config.set(section, PROP_READER_COMPONENT, 'powerdistribution')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/epowerdistributiontl-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'abt-trx'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'abt-trx')
    config.set(section, PROP_READER_COMPONENT, 'abt-trx')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/abt-trx-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
    
    section=SECTION_READER+'credito'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'credito')
    config.set(section, PROP_READER_COMPONENT, 'credito')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/credito-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')  
    
    section=SECTION_READER+'credito-bpmprocess'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'credito-bpmprocess')
    config.set(section, PROP_READER_COMPONENT, 'credito-bpmprocess')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/credito-bpmprocess-core.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')     
    
    section=SECTION_READER+'smappmanager-web'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'smappmanager-web')
    config.set(section, PROP_READER_COMPONENT, 'smappmanager-web')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/smappmanager-web.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'smscada-web'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'smscada-web')
    config.set(section, PROP_READER_COMPONENT, 'smscada-web')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/smscada-web.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'previapp-web'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'previapp-web')
    config.set(section, PROP_READER_COMPONENT, 'previapp-web')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/previapp-web.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')  
    
    section=SECTION_READER+'smicetex-web'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'smicetex-web')
    config.set(section, PROP_READER_COMPONENT, 'smicetex-web')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/smicetex-web.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')

    section=SECTION_READER+'integrator-ws'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'integrator-ws')
    config.set(section, PROP_READER_COMPONENT, 'integrator-ws')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/integrator-ws.debug.log')
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')  

#==============================================================================
#
#==============================================================================     
    
    section=SECTION_READER+'transfer'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'transfer')      
    config.set(section, PROP_READER_COMPONENT, 'transfer')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/transfer-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')  

    section=SECTION_READER+'batchmanager'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'batchmanager')      
    config.set(section, PROP_READER_COMPONENT, 'batchmanager')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/batchmanager-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser') 
    
    section=SECTION_READER+'custommodel'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'custommodel')      
    config.set(section, PROP_READER_COMPONENT, 'transfer')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/custommodel-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser') 

    section=SECTION_READER+'devinterface-trx'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'devinterface-trx')      
    config.set(section, PROP_READER_COMPONENT, 'devinterface-trx')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/devinterface-trx-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')     
    
    section=SECTION_READER+'custommodel-bpmprocess'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'custommodel-bpmprocess')      
    config.set(section, PROP_READER_COMPONENT, 'custommodel-bpmprocess')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/custommodel-bpmprocess-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')     
    
    section=SECTION_READER+'smdemo-web'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'smdemo-web')      
    config.set(section, PROP_READER_COMPONENT, 'smdemo-web')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/smdemo-web.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')    
    
       
#==============================================================================
#
#==============================================================================     
    
    section=SECTION_READER+'smentity'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'smentity')    
    config.set(section, PROP_READER_COMPONENT, 'smentity')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/smentity-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')  

    section=SECTION_READER+'devicetypetok'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'devicetypetok')      
    config.set(section, PROP_READER_COMPONENT, 'devicetypetok')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/devicetypetok-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')
    
    section=SECTION_READER+'security'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'security')      
    config.set(section, PROP_READER_COMPONENT, 'security')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/security-core.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser')    
    
    section=SECTION_READER+'web'
    config.add_section(section)
    config.set(section, PROP_READER_ENABLE, str(True))
    config.set(section, PROP_READER_KEY, 'web')      
    config.set(section, PROP_READER_COMPONENT, 'web')
    config.set(section, PROP_READER_SOURCEFILEPATH, '/sm/log/appcode-web.debug.log') 
    config.set(section, PROP_READER_MODULENAME, 'log4j_parser')
    config.set(section, PROP_READER_CLASSNAME, 'Log4jParser') 
    
    
#==============================================================================
#
#==============================================================================      
    
    
    config.add_section(SECTION_MONITORS_LIST)
    config.set(SECTION_MONITORS_LIST, PROP_MONITORS_ENABLE, str(False))
    config.set(SECTION_MONITORS_LIST, PROP_MONITORS_LIST, 'host-app,ms-device') 
#    config.set(SECTION_MONITORS_LIST, PROP_MONITORS_LIST, 'host,microservice-device,tomcat,postgres') 
#    config.set(SECTION_COMPONENT_MONITORS_LIST, PROP_READER_COMPONENT_MONITORS, 'microserviceregister,security,alarm,web,parameter,audit,concurrent,device,devicetypetok,notification,transaction,directory,location,smentity') 
#    config.set(SECTION_COMPONENT_MONITORS_LIST, PROP_READER_COMPONENT_MONITORS, 'microserviceregister,account,smsecurity,alarm,bpm,integrator,parameter,audit,concurrent,device,notification,transaction,directory,location,etl,evaluation,integrator,operationlog,reporttemplate,user,emailreceiver,healthcampaign,databuffer,powerdistribution,abt-trx,credito,credito-bpmprocess,smappmanager-web,smscada-web,previapp-web,smicetex-web,integrator-ws') 
#    config.set(SECTION_COMPONENT_MONITORS_LIST, PROP_READER_COMPONENT_MONITORS, 'microserviceregister,account,smsecurity,alarm,bpm,integrator,parameter,audit,concurrent,device,notification,transaction,directory,location,etl,evaluation,integrator,operationlog,reporttemplate,user,emailreceiver,databuffer,transfer,batchmanager,custommodel,devinterface-trx,custommodel-bpmprocess,smdemo-web') 
 
    section=SECTION_MONITOR+'host-app'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'host-app')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'device,smsecurity')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_HOST)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, '')
    config.set(section, PROP_MON_HOST, '127.0.0.1')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, '')
    config.set(section, PROP_MON_PWD, '') 
    
    section=SECTION_MONITOR+'tomcat'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'tomcat')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'smdemo-web')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_TOMCAT)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'http://127.0.0.1:8080/SMmng')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'smTomcat')
    config.set(section, PROP_MON_PWD, 'smOsp2012')  
    
    section=SECTION_MONITOR+'ps-account'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ps-account')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'account')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_POSTGRES)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, '')
    config.set(section, PROP_MON_HOST, '127.0.0.1')
    config.set(section, PROP_MON_PORT, '5432')
    config.set(section, PROP_MON_USER, 'sm')
    config.set(section, PROP_MON_PWD, '1234')       
    
    section=SECTION_MONITOR+'ms-account'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-account')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'account')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'account')
    config.set(section, PROP_MON_PWD, 'osp123') 
       
    
    section=SECTION_MONITOR+'ms-smsecurity'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-smsecurity')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'smsecurity')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'smsecurity')
    config.set(section, PROP_MON_PWD, 'osp123') 
    

    section=SECTION_MONITOR+'ms-alarm'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-alarm')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'alarm')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'alarm')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-bpm'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-bpm')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'bpm')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'bpm')
    config.set(section, PROP_MON_PWD, 'osp123')     
       
    section=SECTION_MONITOR+'ms-integrator'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-integrator')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'integrator')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'integrator')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-parameter'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-parameter')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'parameter')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'parameter')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-audit'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-audit')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'audit')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'audit')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-concurrent'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-concurrent')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'concurrent')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'concurrent')
    config.set(section, PROP_MON_PWD, 'osp123')     
     
    section=SECTION_MONITOR+'ms-device'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-device')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'device')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'device')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-notification'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-notification')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'notification')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'notification')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-transaction'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-transaction')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'transaction')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'transaction')
    config.set(section, PROP_MON_PWD, 'osp123')       
    
    section=SECTION_MONITOR+'ms-directory'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-directory')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'directory')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'directory')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-location'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-location')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'location')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'location')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-etl'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-etl')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'etl')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'etl')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-evaluation'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-evaluation')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'evaluation')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'evaluation')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-operationlog'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-operationlog')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'operationlog')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'operationlog')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-reporttemplate'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-reporttemplate')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'reporttemplate')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'reporttemplate')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-user'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-user')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'user')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'user')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-emailreceiver'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-emailreceiver')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'emailreceiver')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'emailreceiver')
    config.set(section, PROP_MON_PWD, 'osp123') 


    section=SECTION_MONITOR+'ms-databuffer'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-databuffer')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'databuffer')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'databuffer')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-transfer'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-transfer')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'transfer')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'transfer')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-batchmanager'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-batchmanager')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'batchmanager')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'batchmanager')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-custommodel'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-custommodel')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'custommodel')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'custommodel')
    config.set(section, PROP_MON_PWD, 'osp123') 
    
    section=SECTION_MONITOR+'ms-devinterface-trx'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-devinterface-trx')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'devinterface-trx')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'devinterface-trx')
    config.set(section, PROP_MON_PWD, 'osp123') 

    section=SECTION_MONITOR+'ms-custommodel-bpmprocess'
    config.add_section(section)
    config.set(section, PROP_MON_ENABLE, str(True)) 
    config.set(section, PROP_MON_KEY, 'ms-custommodel-bpmprocess')      
    config.set(section, PROP_MON_COMPONENT_LIST, 'custommodel-bpmprocess')
    config.set(section, PROP_MON_TYPE, MONITOR_TYPE_SPRINGMICROSERVICE)
    config.set(section, PROP_MON_INTERVAL, '15.0')
    config.set(section, PROP_MON_URL, 'https://127.0.0.1:4016/management/metrics')
    config.set(section, PROP_MON_HOST, '')
    config.set(section, PROP_MON_PORT, '0')
    config.set(section, PROP_MON_USER, 'custommodel-bpmprocess')
    config.set(section, PROP_MON_PWD, 'osp123') 
           
    
    saveConfig(config)
    

if __name__ == '__main__':
    createDefaultConfigfile()
    config=loadConfig()     
    printConfig(config)