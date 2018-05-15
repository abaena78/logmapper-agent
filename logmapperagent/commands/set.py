# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:43:08 2017

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
import logmapperagent.utils.thread_util as thutil
from enum import Enum


logger = logging.getLogger(__name__)


    
    
class SET_OPTION(Enum):
    DATA_SEND =0
    SAVE_EVENTS=1
    

class SetCommand(cli.LogMapperCommandDefinition):
   
    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        if not self.arg1:
            return cli.LogMapperCommandResponse(False, "Invalid option")
        
        if len(self.args) < 2:
            return cli.LogMapperCommandResponse(False, "Missing parameters") 
        
        opt = self.args[1]
        if opt == '1':
            value = True
        elif opt == '0':
            value = False
        else:
            return cli.LogMapperCommandResponse(False, "Invalid parameter: "+opt)        
        
        if self.arg1 == 'ds':
            setReaderThreads(config, SET_OPTION.DATA_SEND, value)
            setMonitorThreads(config, SET_OPTION.DATA_SEND, value)
            return cli.LogMapperCommandResponse(True, "Set OK") 
        
        if self.arg1 == 'se':
            setReaderThreads(config, SET_OPTION.SAVE_EVENTS, value)
            return cli.LogMapperCommandResponse(True, "Set OK")        
        
        return cli.LogMapperCommandResponse(False, "Invalid option")
    
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    commandDefinition = SetCommand("set", "s", "Help")
    commandDefinition.parseArgs("set ") 
    response = commandDefinition.execute()
    print(str(response))
    
    print("End module execution")
    
    
    
def setReaderThreads(config, cmd, value):
    readers = cfg.getReaders(config)
    for readerName in readers:
        readerConfig = cfg.loadReaderConfig(config, readerName)
        readerThread = thutil.getThread(cfg.THREAD_READER+readerConfig.key)
        applyOptionInThread(readerThread, cmd, value)
            
    
def setMonitorThreads(config, cmd, value):
    monitors = cfg.getMonitors(config)
    for key in monitors:
        monitorConfig = cfg.loadMonitorConfig(config, key)
        monitorThread = thutil.getThread(cfg.THREAD_MONITOR+monitorConfig.key)
        applyOptionInThread(monitorThread, cmd, value)
            
def applyOptionInThread(lmThread, cmd, value):
    if not lmThread:
        return
    if cmd == SET_OPTION.DATA_SEND:
        lmThread.enableDataSend = value
    elif cmd == SET_OPTION.SAVE_EVENTS:
        lmThread.enableSaveEvents = value        