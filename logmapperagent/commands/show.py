# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:42:58 2017

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
import datetime
import os
import psutil
import platform
import socket

import config.config as cfg
import logmapperagent.control.cli as cli


logger = logging.getLogger(__name__)


class ShowCommand(cli.LogMapperCommandDefinition):
  
    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """
        logger.debug("execute")
        if not self.arg1:
            response = cmdStatus()
            logger.debug("execute response:"+response)
            return cli.LogMapperCommandResponse(True, response)
        
        if self.arg1 == 'status':
            response = cmdStatus()
            return cli.LogMapperCommandResponse(True, response)  

        if self.arg1 == 'readers':
            response = cmdReaderStatus()
            return cli.LogMapperCommandResponse(True, response)         
        
        if self.arg1 == 'host':
            response = commandHostStatus()
            return cli.LogMapperCommandResponse(True, response)     
        
        if self.arg1 == 'cfg':
            response = cmdConfig(config)
            return cli.LogMapperCommandResponse(True, response) 

        return cli.LogMapperCommandResponse(False, 'Invalid option')          
    
    
    
    
def cmdStatus():
    """ 
    ===========================================================================
    Summary 
    ===========================================================================   
    
    **Args**:
        arg1
    **Returns**:
        None
    """     
    response= 'LogMapperAgent State ' +str(datetime.datetime.now())+"\r\n"
    response += "\r\nReaders\r\n" 
    data = ( "Name", "StartDate", "Count", "Records", "Bytes", "Fails", "State" )
    response += "{:<40} {:<30} {:<12} {:<12} {:<12} {:<12} {:<20}\r\n".format( *data )      
    for t in threading.enumerate():
        if not (cfg.THREAD_READER in t.getName()) :
            continue
        data = ( t.getName(), str(t.startDate), str(t.loopCount), str(t.recordsProcessed), str(t.bytesProcessed), str(t.fails), str(t.getState()) )
        response += "{:<40} {:<30} {:<12} {:<12} {:<12} {:<12} {:<20}\r\n".format( *data )  
    
    response += "\r\nMonitors\r\n"
    data = ( "Name", "StartDate", "Count", "Records", "Bytes", "Fails", "State" )
    response += "{:<40} {:<30} {:<12} {:<12} {:<12} {:<12} {:<20}\r\n".format( *data )    
    for t in threading.enumerate():
        if not (cfg.THREAD_MONITOR in t.getName()) :
            continue
        data = ( t.getName(), str(t.startDate), str(t.loopCount), str(t.recordsProcessed), str(t.bytesProcessed), str(t.fails), str(t.getState()) )
        response += "{:<40} {:<30} {:<12} {:<12} {:<12} {:<12} {:<20}\r\n".format( *data )        

    response += "\r\nOther threads\r\n"
    for t in threading.enumerate():
        if not (cfg.THREAD_MAPPER in t.getName()) :
            continue
        data = ( t.getName(), str(t.startDate), str(t.getState()) )
        response += "{:<40} {:<30} {:<30}\r\n".format( *data )   
        
    for t in threading.enumerate():
        if not (cfg.THREAD_SAVEDB in t.getName()) :
            continue
        data = ( t.getName(), str(t.startDate) )
        response += "{:<40} {:<30}\r\n".format( *data )         
    
    
    return response

def cmdReaderStatus():
    response= 'LogMapperAgent Reader State ' +str(datetime.datetime.now())+"\r\n" 
    for t in threading.enumerate():
        if not (cfg.THREAD_READER in t.getName()) :
            continue
        

        response += "\r\n" 
        response += "\r\nName:             "+t.getName()
        response += "\r\n"+str(t.readerConfig)        
        response += "\r\n startDate:       "+str(t.startDate)
        response += "\r\n loopCount:       "+str(t.loopCount)
        response += "\r\n recordsProcessed:"+str(t.recordsProcessed)
        response += "\r\n bytesProcessed:  "+str(t.bytesProcessed)
        response += "\r\n countPathsFound: "+str(t.countPathsFound)
        response += "\r\n fails:           "+str(t.fails)
        response += "\r\n state:           "+str(t.getState())
        response += "\r\n enableSaveEvents:"+str(t.enableSaveEvents)
        response += "\r\n enableDataSend:  "+str(t.enableDataSend)  
        response += "\r\n nextSaveDataDate:"+str(t.nextSaveDataDate)
        response += "\r\n lastTruncateDate:"+str(t.lastTruncateDate)
        
        if t.errorDetail:
            response += "\r\n errorDetail:     "+str(t.errorDetail)
 

        
    return response

def cmdConfig(config):
    """ 
    ===========================================================================
    Summary 
    ===========================================================================   
    
    **Args**:
        arg1
    **Returns**:
        None
    """     
    response= '\n\r'
    for section in config.sections():
        for key in config[section]: 
            data = ( section+'.'+key, config.get(section, key) )
            response += "{:<60} = {:<40}\r\n".format( *data )               
    return response

def commandHostStatus():
    formatstr = "{:<30} = {:<40}\r\n"
    response= '\n\r'
    response += formatstr.format( "threading.activeCount()", str(threading.activeCount()) )
    response += formatstr.format( "os.name", os.name )
    response += formatstr.format( "platform.system()", platform.system() )
    response += formatstr.format( "platform.release()", platform.release() )
    response += formatstr.format( "datetime.now()", str(datetime.datetime.now()) )
    response += formatstr.format( "os.getcwd()", os.getcwd() )
    response += formatstr.format( "socket.gethostname()", socket.gethostname() )
    response += formatstr.format( "psutil.cpu_percent()", str(psutil.cpu_percent()) )
    response += formatstr.format( "psutil.cpu_times_percent()", str(psutil.cpu_times_percent()) )
    response += formatstr.format( "len(psutil.pids())", str(len(psutil.pids())) )
    response += formatstr.format( "psutil.virtual_memory()", str(psutil.virtual_memory()) )
    response += formatstr.format( "psutil.disk_usage()", str(psutil.disk_usage(os.getcwd())) )
    response += formatstr.format( "psutil.disk_io_counters()", str(psutil.disk_io_counters()) )
    response += formatstr.format( "len(psutil.net_connections())", str(len(psutil.net_connections())) )
    response += formatstr.format( "psutil.net_io_counters()", str(psutil.net_io_counters()) )
    return response
    
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    commandDefinition = ShowCommand("show", "sh", "Help")
    commandDefinition.parseArgs("show host") 
    response = commandDefinition.execute()
    print(str(response))
    
    print("End module execution")