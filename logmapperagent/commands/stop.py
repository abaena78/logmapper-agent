# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:41:45 2017

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
import threading

import logmapperagent.control.cli as cli
import config.config as cfg
import logmapperagent.utils.thread_util as thutil


logger = logging.getLogger(__name__)

#%%
#==============================================================================
# Global Initialization. cfgants definitions.
#==============================================================================

logger = logging.getLogger(__name__)


class StopCommand(cli.LogMapperCommandDefinition):
       
    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        if not self.arg1:
            return cli.LogMapperCommandResponse(False, "Invalid option")
         
        if self.arg1 == 'logmapper':
            return cli.LogMapperCommandResponse(True, "Stopping Logmapper...")
        
        if self.arg1 == 'threads':
            stopThreads(config)
            return cli.LogMapperCommandResponse(True, "Threads stopped")
        
        if self.arg1 == 'reader' and len(self.args) == 2: 
            key = self.args[1]
            stopReader(key)
            return cli.LogMapperCommandResponse(True, "Thread stopped") 
        
        if self.arg1 == 'readers':
            stopReaderThreads(config)
            return cli.LogMapperCommandResponse(True, "Readers stopped") 

        if self.arg1 == 'monitors':
            stopMonitorThreads(config)
            return cli.LogMapperCommandResponse(True, "Monitors stopped")         
        
        return cli.LogMapperCommandResponse(False, "Invalid option")
    

def stopReader(key):
    readerThread = thutil.getThread(cfg.THREAD_READER+key)
    if readerThread: readerThread.stopRun() 
        
def stopReaderThreads(config):
    readers = cfg.getReaders(config)
    for readerName in readers:
        readerConfig = cfg.loadReaderConfig(config, readerName)
        readerThread = thutil.getThread(cfg.THREAD_READER+readerConfig.key)
        if readerThread: readerThread.stopRun()     
    
def stopMapperThreads(config):
    readers = cfg.getReaders(config)
    for readerName in readers:
        readerConfig = cfg.loadReaderConfig(config, readerName)
        mapperThread = thutil.getThread(cfg.THREAD_MAPPER+readerConfig.key)
        if mapperThread: mapperThread.stopRun() 
    
def stopMonitorThreads(config):
    monitors = cfg.getMonitors(config)
    for key in monitors:
        monitorConfig = cfg.loadMonitorConfig(config, key)
        monitorThread = thutil.getThread(cfg.THREAD_MONITOR+monitorConfig.key)
        if monitorThread: monitorThread.stopRun()    

    

def stopThreads(config):
    """ 
    ===========================================================================
    Summary 
    ===========================================================================   
    
    **Args**:
        arg1
    **Returns**:
        None
    """     
    logger.info("Finish Threads") 
 
    stopMapperThreads(config)
    
    stopReaderThreads(config)
    
    stopMonitorThreads(config)
    
       
    #Wait finish threads
    for t in threading.enumerate():
        if not (cfg.THREAD_PREFIX in t.getName()) :
            continue
        logging.debug('Wait finish %s', t.getName())
        t.join()  
        
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    commandDefinition = StopCommand("stop", "sto", "Help")
    commandDefinition.parseArgs("stop logmapper") 
    response = commandDefinition.execute()
    print(str(response))
    
    print("End module execution")        