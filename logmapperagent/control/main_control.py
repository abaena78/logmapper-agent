#!/usr/bin/python3
# -*- coding: utf-8 -*-

#LogMapper
#
#MIT License
#
#Copyright (c) 2018 Jorge A. Baena - abaena78@gmail.com
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""
Main Control Loop for LogMapper Agent

Start Main Threads: cli, server.
Manage the message flow control beetween threads

@author: Andres Baena
@contact    : www.logmapper.org
@copyright: "Copyright 2017, The LogMapper Project"
@license: "GPL"
@date:    15/09/2017
@version: 1.0.0
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************

import time
import logging


import config.config as cfg
import logmapperagent.control.server_handler as srv
import logmapperagent.control.cli as cli
import logmapperagent.commands as cmd
import logmapperagent.utils.thread_util as thutil


#%%
#==============================================================================
# Global Initialization. cfgants definitions.
#==============================================================================

logger = logging.getLogger(__name__)


#%%
    
def initApplication(config):
    pass
    
def startApplicationTask(config):
    
    if config.getboolean(cfg.SECTION_MONITORS_LIST, cfg.PROP_MONITORS_ENABLE): 
        cmd.start.startMonitorsThreads(config) 

    if config.getboolean(cfg.SECTION_READERS_LIST, cfg.PROP_READERSENABLE): 
        cmd.start.startReadersThreads(config) 
     
    if config.getboolean(cfg.SECTION_LOGMAPPER, cfg.PROP_ENABLESENDDATA):
        registerInMaster(config)
        

def stopApplicationTask(config): 
    cmd.stop.stopThreads(config)  
 

def registerInMaster(config):  
    r = ""
    tries = 0
    while (not "success" in r) and tries < 20:    
        try:
            time.sleep(10)
            r = cmd.start.startRegister(config)
            logger.debug("register:"+r)
            tries += 1 
        except Exception as exc:
            logger.warning("Master connect error:"+str(exc)) 
            tries += 1
     

#%%
    

#%%
def mainLoop(config): 
    """ 
    ===========================================================================
    logmappper-agent **Main** function 
    ===========================================================================   
    Aqui un ejemplo de documentacion
    Formatos: *cursiva* 
    ``code = True``
    
    **Args**:
        config: configuration object
        
    **Returns**:
        None
    
    """
    logger.info("Start mainLoop")
    
    port = config.getint(cfg.SECTION_LOGMAPPER, cfg.PROP_AGENTPORT)
    socketServerThread = srv.SocketServerThread(cfg.SOCKET_SERVER_THREAD_KEY, port)
    socketServerThread.start() 
    
    while True:
        time.sleep(0.25)
          
        if not srv.queueRxSocketServer.empty():
            inputData = srv.queueRxSocketServer.get()
                
            try:
                commandDefinition = cli.getCommandDefinition(inputData, cmd.commands_index.COMMAND_LIST)
                commandDefinition.parseArgs(inputData)
                response = commandDefinition.execute(config)
            except Exception as exc:
                logger.exception("Exception in executing command: "+str(inputData))
                response = cli.LogMapperCommandResponse(False, str(exc))
            
            srv.queueTxSocketServer.put(response)           
            if commandDefinition.command == 'stop' and commandDefinition.arg1 == 'logmapper':
                logger.debug("Stopping logmapper")
                break            
            
    socketServerThread.stopRun()
    srv.checkServerClosed()
    
    logger.debug("Finish mainLoop")

#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

    cfg.createDefaultConfigfile()
    config=cfg.loadConfig()    
    mainLoop(config)  
    
    print("End module execution")    
    

