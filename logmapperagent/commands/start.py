 # -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 13:06:12 2017

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************
import logging

import logmapperagent.control.cli as cli
import config.config as cfg
import logmapperagent.utils.thread_util as th
import logmapperagent.reader.reader as reader
import logmapperagent.reader.mapper as mapper
import monitors.host.monitor_host as monhost
import monitors.microservices.monitor_microservices as monmicroserv
import monitors.tomcat.monitor_tomcat as montomcat
import monitors.postgres.monitor_postgres as monpsql

import logmapperagent.commands.get as get
import logmapperagent.utils.datasender as ds
import logmappercommon.definitions.logmapperkeys as lmkey
import logmapperagent.utils.thread_util as thutil


logger = logging.getLogger(__name__)

class StartCommand(cli.LogMapperCommandDefinition):
 
    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        if not self.arg1:
            return cli.LogMapperCommandResponse(False, "Invalid option")        
        
        if self.arg1 == 'map':
            if len(self.args) < 2: return cli.LogMapperCommandResponse(False, "Invalid arguments")
            #TODO MEJOR FORMA DE SELECCIONAR KEY
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            mapperThread = mapper.MapperThread(readerConfig, readerConfig)
            mapperThread.start()             
            
            return cli.LogMapperCommandResponse(True, "Mapper started") 
        
        if self.arg1 == 'readers':
            startReadersThreads(config)
            return cli.LogMapperCommandResponse(True, "All readers started")         
        
        if self.arg1 == 'mappers':
            startMapperThreads(config)
            return cli.LogMapperCommandResponse(True, "All mappers started") 
        
        if self.arg1 == 'monitors':
            startMonitorsThreads(config)
            return cli.LogMapperCommandResponse(True, "All monitors started")         
        
        if self.arg1 == 'register':
            return cli.LogMapperCommandResponse(True, startRegister(config))         
        
        return cli.LogMapperCommandResponse(False, "Invalid option")
    
def startMonitorsThreads(config):
    """ 
    ===========================================================================
    Summary 
    ===========================================================================   
    
    **Args**:
        arg1
    **Returns**:
        None
    """     
    monitors = cfg.getMonitors(config)
    for key in monitors:
        monitorConfig = cfg.loadMonitorConfig(config, key)

        monitorThread = thutil.getThread(cfg.THREAD_MONITOR+monitorConfig.key)
        
        if monitorThread:
            logger.debug("Thread already running:"+monitorConfig.key)
            continue        
        
        if monitorConfig.enable:
            if monitorConfig.type == cfg.MONITOR_TYPE_HOST:
                monitorThread = monhost.MonitorHostThread(monitorConfig, th.OperationMode.NORMAL)
                monitorThread.start() 
            elif monitorConfig.type == cfg.MONITOR_TYPE_SPRINGMICROSERVICE:
                monitorThread = monmicroserv.MonitorMicroserviceThread(monitorConfig, th.OperationMode.NORMAL)
                monitorThread.start() 
            elif monitorConfig.type == cfg.MONITOR_TYPE_TOMCAT:
                monitorThread = montomcat.MonitorTomcatThread(monitorConfig, th.OperationMode.NORMAL)
                monitorThread.start()
            elif monitorConfig.type == cfg.MONITOR_TYPE_POSTGRES:
                monitorThread = monpsql.MonitorPostgresThread(monitorConfig, th.OperationMode.NORMAL)
                monitorThread.start()                
            else:
                logger.error("Invalid monitor type :"+str(monitorConfig.type))
         
            
def startReadersThreads(config):
    """ 
    ===========================================================================
    Summary 
    ===========================================================================   
    
    **Args**:
        arg1
    **Returns**:
        None
    """     
    # Start Readers Threads    
    readers = cfg.getReaders(config)
    for key in readers:
        readerConfig = cfg.loadReaderConfig(config, key)
        readerThread = thutil.getThread(cfg.THREAD_READER+readerConfig.key)
        
        if readerThread:
            logger.debug("Thread already running:"+readerConfig.key)
            continue
        
        if readerConfig.enable:
            readerThread = reader.ReaderThread(readerConfig, th.OperationMode.NORMAL)
            readerThread.start()             

def startMapperThreads(config):
    """ 
    ===========================================================================
    Summary 
    ===========================================================================   
    
    **Args**:
        arg1
    **Returns**:
        None
    """    
    readers = cfg.getReaders(config)
    for readerName in readers:
        readerConfig = cfg.loadReaderConfig(config, readerName)
        if readerConfig.enable:
            mapperThread = mapper.MapperThread(readerConfig, th.OperationMode.NORMAL)
            mapperThread.start() 
            
            
def startRegister(config):
    agentConfig = cfg.loadLogMapperAgentConfig(config)
    j = get.getAgent(config)
    r = ds.saveData(agentConfig.masterHost, agentConfig.masterPort, lmkey.DATATYPE_AGENT, j)
    return str(r)       
    
    
        
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    cfg.createDefaultConfigfile()
    config=cfg.loadConfig()    
    
    commandDefinition = StartCommand("start", "sta", "Help")
    commandDefinition.parseArgs("start register") 
    response = commandDefinition.execute(config)
    print(str(response))
    
    print("End module execution")    