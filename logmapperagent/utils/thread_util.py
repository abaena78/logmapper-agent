# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 13:15:12 2017

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
from enum import Enum
import datetime
import time

import logmappercommon.utils.logmapper_util as lmutil

logger = logging.getLogger(__name__)

#%%
#==============================================================================
# 
#==============================================================================


class ThreadState(Enum):
    CREATED = 0    
    STARTING = 1
    PROCESSING = 2
    IDLE = 3
    ENDING=4
    ENDED=5
    ERROR = 99
    
class OperationMode(Enum):
    NORMAL = 0
    TEST = 1
    
class ActionState(Enum):
    IDLE = 0
    PENDING = 1
    EXECUTING = 2 


class LogMapperThread(threading.Thread):
    """ 
    ===========================================================================
    Thread Class for general purpose
    ===========================================================================   
    
    **Methods**:
        start: (from Thread): Start Thread. Call run method
        stopRun: safe stop of the thread
    **Attributes**:
        None
    """ 
    def __init__(self, category, key, operationMode = OperationMode.NORMAL):
        threading.Thread.__init__(self)
        self.setName(category+key)
        self.key = key
        self.operationMode = operationMode 
        self._stopRun = False
        self._state = ThreadState.CREATED
        self.errorDetail = None
        self._action = None
        self._actionState = ActionState.IDLE
        self.startDate = None
        self.endDate = None
        self.loopCount = 0
        self.loopCountBefore = 0
        self.bytesProcessed = 0
        self.bytesProcessedBefore = 0
        self.recordsProcessed = 0
        self.recordsProcessedBefore = 0
        self.fails = 0
        self.failsBefore = 0        
        self.currentDate = None
        self.nextSaveDataDate = None
        self.enableDataSend = True
        
    def getCounters(self):
        d = {
                'count' : self.loopCount - self.loopCountBefore,
                'bytes' : self.bytesProcessed - self.bytesProcessedBefore,
                'records' : self.recordsProcessed - self.recordsProcessedBefore,
                'fails' : self.fails - self.failsBefore,
                }
        self.loopCountBefore = self.loopCount
        self.bytesProcessedBefore = self.bytesProcessed
        self.recordsProcessedBefore = self.recordsProcessed
        self.failsBefore = self.fails
        return d
        
    def stopRun(self):
        """
        Ask thread end safely
        """
        logger.debug("stopRun:"+self.name)
        self._stopRun = True 
     
    def setState(self, state):
        logger.debug("setState:"+self.name+':'+str(state))
        self._state = state
        
    def getState(self):
        logger.debug("getState:"+self.name+':'+str(self._state))
        return self._state   
    
    def setStateError(self, errorDetail):
        logger.error("setStateError:"+errorDetail)
        self.setState(ThreadState.ERROR) 
        self.errorDetail = errorDetail
        
    def startAction(self, action):
        logger.debug("setAction:"+action)
        if self._actionState != ActionState.IDLE:
            return "BUSY"
        self._action = action
        self._actionState = ActionState.PENDING 
        return "OK"
    
    def getActionState(self):
        logger.debug("getActionState:"+str(self._actionState))
        return (self._action, self._actionState)     
                   
    def run(self):
        logger.debug ("Start Thread:" + self.name)  
        try:
            self.setState(ThreadState.STARTING)
            self.startDate=datetime.datetime.now()
            self.currentDate = datetime.date.today()
            self.nextSaveDataDate = lmutil.getNextLogMapperIntervalDate(self.startDate)
            self.process()
            self.setState(ThreadState.ENDED)
            self.endDate = datetime.datetime.now()
        except Exception as exc:
            self.setStateError(str(exc))
            logger.exception("Exception in "+self.name)     
            
        logger.debug ("End Thread:" + self.name)  

    def process(self):
        logger.debug("process:")
        
        self.setState(ThreadState.PROCESSING)
        while not self._stopRun:  
            self.loopCount += 1
            time.sleep(10)
        self.setState(ThreadState.ENDING)         
            
#%%
#==============================================================================
# 
#==============================================================================            

def getThread(name):
    """ 
    ===========================================================================
    Search in All Active Threads. Return the Thread Class with the same name 
    ===========================================================================   
    
    **Args**:
        name (str): name of the thread that is looking
    **Returns**:
        Thread object. None if it is not found
    """ 
    logger.debug('getThread:'+name)          
    for t in threading.enumerate():
        if t.getName() == name:
           return t
    return None

#%%
"""
*******************************************************************************
Module Execution
This code helps to developer to know the usage of the module
*******************************************************************************
"""
if __name__ == '__main__':    
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S') 
    