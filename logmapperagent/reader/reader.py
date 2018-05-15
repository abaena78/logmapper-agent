# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 15:52:27 2018

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************
    
import os
import logging
import time
import datetime

import config.config as cfg
import logmappercommon.utils.sqlite_util as db
import logmappercommon.utils.logmapper_util as lmutil
import logmapperagent.reader.logmapper_dao as lmdao
import logmapperagent.reader.logmapper_events_dao as eventdao
import logmapperagent.commands.get as get
import logmapperagent.utils.thread_util as th
import logmapperagent.utils.datasender as ds
from logmappercommon.definitions.event_categories import LogEventCategories
import logmappercommon.definitions.logmapperkeys as lmkey

#%%
"""
Global Initialization. cfgants definitions.
"""

logger = logging.getLogger(__name__)


TRUNCATE_COUNT = 100000        


class ReaderThread(th.LogMapperThread):
    """ 
    ===========================================================================
    Thread Class for read one log file 
    ===========================================================================   
    
    **Methods**:
        start: (from Thread): Start Thread. Call run method
        stopRun: safe stop of the thread
    **Attributes**:
        None
    """ 
    
    
    
    def __init__(self, readerConfig, operationMode):
        th.LogMapperThread.__init__(self, cfg.THREAD_READER, readerConfig.key, operationMode)    
        self.readerConfig=readerConfig
        self.countPathsFound = 0
        self.enableSaveEvents = False
        self.enableDataSend = self.readerConfig.enableSendData
        self.lastTruncateDate = None
                    
        
    def follow(self, filepath):
        """ 
        ===========================================================================
        Read new lines of file like tail -f 
        non blocking function
        ===========================================================================   
        
        **Args**:
            filepath: file to follow
        **Yields**:
            line: new line readed
        """  
        f = open(filepath)
        currentInode = os.fstat(f.fileno()).st_ino
        f.seek(0, 2)
        while not self._stopRun:
            # execute actions requested by main control
            # this functionis here because this is a non blocking loop
#            self.actionHandler()
            
            line = f.readline()
            if not line:
                try:
                    if os.stat(filepath).st_ino != currentInode:
                        f.close()
                        f = open(filepath)
                        currentInode = os.fstat(f.fileno()).st_ino
                        logger.debug("Reopen file:"+filepath)
                        continue
                except IOError:
                    pass                
                time.sleep(0.2)
            else:
                yield line
        f.close()  
    


    def process(self):
        #======================================================================
        # Runtime search of the parser class
        #======================================================================
        module = __import__('parsers.'+self.readerConfig.moduleName, fromlist=[''])
        class_ = getattr(module, self.readerConfig.className)
        parser = class_(self.readerConfig.hostname, self.readerConfig.component)
        if not parser:
            self.setStateError("Parser class not found["+self.name+"]"+self.readerConfig.className)
            return 

        #======================================================================
        # Check logger file exist. If not wait
        #======================================================================                        
        while (not self._stopRun) and (not os.path.isfile(self.readerConfig.sourcefilepath) ):
            logger.debug("File not exist. Wait: "+self.readerConfig.sourcefilepath)
            time.sleep(10) 
            
        connDbMemory=db.connectDbMemory() 
        cursor = connDbMemory.cursor()            
            
        #======================================================================
        # Create events database if not exist
        # If exist get last index
        #======================================================================  
        
        #db.deleteDbFile(self.readerConfig.dbEventsPath)
        connDbEvents = db.connectDb(self.readerConfig.dbEventsPath)
        cursorDbEvents = connDbEvents.cursor()
        eventdao.createTablesEvents(cursorDbEvents)
        connDbEvents.commit()          
        
        db.copyDbData(connDbEvents, connDbMemory) 
        connDbMemory.commit()        
        
        cursorDbEvents.close()
        connDbEvents.close()           
            
        #======================================================================
        # Create base tables if not exist
        # If exist load data into db in memory
        # truncate events table in memory. Set id sequence
        #====================================================================== 
        connDbBase=db.connectDb(self.readerConfig.dbBasePath)
        cursorDbBase = connDbBase.cursor()
        lmdao.createTablesBase(cursorDbBase) 
        connDbBase.commit()
        
        db.copyDbData(connDbBase, connDbMemory) 
        connDbMemory.commit()
        
        cursorDbBase.close()
        connDbBase.close()
        
        #======================================================================
        # Database for preprocess data
        #======================================================================         
        #database for measures and events
        connDbData=db.connectDb(self.readerConfig.dbDataPath)
        cursorData = connDbData.cursor()
        lmdao.createTablesData(cursorData)
        connDbData.commit()          
                          
        #======================================================================
        # Set control variables
        #======================================================================        
       
        self.setState(th.ThreadState.PROCESSING)
        
        #======================================================================
        # Main loop
        #======================================================================         
        while not self._stopRun:
            for line in self.follow(self.readerConfig.sourcefilepath):
                self.loopCount += 1
                self.bytesProcessed += len(line)
                #==============================================================
                # If parser was OK, fill other data in object logEvent.
                #==============================================================
                logEvent=parser.parse(line) 
                if logEvent == None:
                    continue
                self.recordsProcessed += 1  
                
                if self.operationMode == th.OperationMode.TEST:
                    logger.debug(str(logEvent))
                    continue
                
                #==============================================================
                # Save logmapper interval measures
                #==============================================================
                now = datetime.datetime.now() 
                if now > self.nextSaveDataDate:
                    self.nextSaveDataDate = lmutil.getNextLogMapperIntervalDate(now)
                    start = lmutil.getBeforeMapperIntervalDate(now)
                    end = lmutil.getLogMapperIntervalDate(now)
                    
                    measures = get.getPathMeasures(cursor, start, end)
                    for m in measures:
                        logger.debug(">>measure:"+str(m))   
                        lmdao.insertPathMeasure(cursorData, date=m[0], path_id=m[1], count=m[2], duration_avg=m[3], duration_std=m[4],duration_max=m[5])
                        
                    logevents = get.getLogEventsCount(cursor, start, end) 
                    for e in logevents:
                        lmdao.insertLogEvent(cursorData, date=e[0] , eventtype=e[2], count=e[3])
                        
                    logMetrics = get.getLogMetrics(cursor, start, end) 
                    for m in logMetrics:
                        lmdao.insertLogMetrics(cursorData, m[0], m[1], m[2], m[3], m[4], m[5], m[6]) 
                        
                    connDbData.commit()
                    
                    
                    if self.enableDataSend:                  
                        j = get.getJsonPathMeasures(self.readerConfig, start, end)
                        j['lmstats'] = self.getCounters()
                        logger.debug("send1:"+str(start)+" - "+str(end))
                        sender = ds.DataSenderThread(self.name, self.readerConfig.masterHost, self.readerConfig.masterPort, lmkey.DATATYPE_PATH_METRICS, j)
                        sender.start() 
                        
                        j = get.getJsonLogEventsCount(self.readerConfig, start, end)
                        logger.debug("send2:"+str(start)+" - "+str(end))
                        sender2 = ds.DataSenderThread(self.name, self.readerConfig.masterHost, self.readerConfig.masterPort, lmkey.DATATYPE_LOG_EVENTS, j)
                        sender2.start() 
                        
                        j = get.getJsonLogMetrics(self.readerConfig, start, end)
                        logger.debug("send3:"+str(start)+" - "+str(end))
                        sender3 = ds.DataSenderThread(self.name, self.readerConfig.masterHost, self.readerConfig.masterPort, lmkey.DATATYPE_LOG_METRICS, j)
                        sender3.start()                     
                        
                        
                #==============================================================
                # check day change, reset memory database
                #==============================================================  
                if self.currentDate != now.date():
                    dayBefore=str(self.currentDate)
                    logger.info('Day end. reset data: '+dayBefore)
                    self.currentDate = datetime.date.today()
                    
                    #Save base db
                    #db.deleteDbFile(self.readerConfig.dbBasePath)  
                    #connDbBase=db.connectDb(self.readerConfig.dbBasePath)
                    #db.copyDbDataSelection(connDbMemory, connDbBase, ['lmp_logPathsT', 'lmp_logNodesT'])              
                    #connDbBase.close()                    
                    
                    #newFile = self.readerConfig.dbEventsPath + "." + dayBefore
                    #connDbEvents = db.connectDb(self.readerConfig.dbEventsPath)
                    #db.copyDbDataSelection(connDbMemory, connDbEvents, ['lmp_logEventsT'])                   
                    #connDbEvents.close()  
                    
                    #db.copyDbFile(self.readerConfig.dbEventsPath, newFile)
                    #db.deleteDbFile(self.readerConfig.dbEventsPath)
                    #connDbEvents=db.connectDb(self.readerConfig.dbEventsPath)
                    #cursorDbEvents = connDbEvents.cursor()
                    #eventdao.createTablesEvents(cursorDbEvents)                     
                    #connDbEvents.close()  
                    
                    #eventdao.truncateTableLogEvents(connDbMemory, currentEventIdUpdated)
                    #connDbMemory.commit()  
                    
                #==============================================================
                # clean events
                #==============================================================  
                if self.recordsProcessed % TRUNCATE_COUNT == 0: 
                    eventdao.truncateTableLogEvents(connDbMemory)
                    connDbMemory.commit() 
                    self.lastTruncateDate = now
                                                
                
                #==============================================================
                # Find logNode, if not exist, it is created
                # If exist, increment counter
                # Vars created: logNodeId, logNodeCategory
                #==============================================================                
                row = lmdao.findLogNodeIdByKey(cursor, logEvent.key)
                if not row:
                    logger.debug("insertLogNode"+str(logEvent))
                    lmdao.insertLogNode(cursor, logEvent)
                    connDbMemory.commit()    
                    logNodeId=cursor.lastrowid
                    logNodeCategory = logEvent.eventCategory.value

                else:
                    lmdao.updateLogNodeCount(cursor, row[0], row[1]+1)
                    connDbMemory.commit() 
                    logNodeId=row[0]
                    logNodeCategory= row[2]
#                    logger.debug("LogNode Found:"+str(logNodeId)+logNodeCategory)

                #==============================================================
                # Find logThreads, if not exist, it is created
                # Vars: logThreadId, logThreadCount, lastLogEventId, path1LogNodeId, path1Exectime
                #==============================================================               
              
                threadKey = logEvent.host + ":"+ logEvent.component +":"+ logEvent.threadKey                
                row = lmdao.findLogThreadByKey(cursor, threadKey)               
                if row:
                    threadCreation=datetime.datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S.%f') 
                    timeEvent=datetime.datetime.strptime(logEvent.timeexec, '%Y-%m-%d %H:%M:%S.%f')
                    duration=timeEvent-threadCreation #datetime.timedelta

                    if duration.seconds > 600:
                        lmdao.setLogThreadInvalid(cursor, threadKey, row[0])
                        row = None
                    else:
                        logThreadId = row[0]
                        logThreadCount = row[1]
                        lastLogEventId = row[2]
                        path1LogNodeId = row[3]
                        path1Exectime = row[4]                   
               
     
                if not row:
                    lmdao.insertLogThread(cursor, threadKey, logEvent.timeexec)
                    connDbMemory.commit() 
                    logThreadId=cursor.lastrowid
                    logThreadCount = 1
                    lastLogEventId = None
                    path1LogNodeId = None
                    path1Exectime = None 
                    
                #==============================================================
                # create logEvent
                # vars: logEventId
                #==============================================================                     
                eventdao.insertLogEvent(cursor, logThreadId, logNodeId, logEvent.timeexec, logEvent.remoteCallKey, logEvent.userKey, lastLogEventId, logNodeCategory)
                connDbMemory.commit() 
                logEventId = cursor.lastrowid 
                
                now = datetime.datetime.now()
                timelog=datetime.datetime.strptime(logEvent.timeexec, '%Y-%m-%d %H:%M:%S.%f') 
                duration=now-timelog #datetime.timedelta                
                
#                logger.debug("logEventId="+str(logEventId)+", delay="+str(duration.seconds))
                if duration.seconds > 5:
                    logger.warning(self.name + ": logEventId="+str(logEventId)+", delay="+str(duration.seconds))
                
                #==============================================================
                # update thread, check relation, search path
                #==============================================================                  

                if logNodeCategory == LogEventCategories.TRACE_MAIN_NODE.value:
                    if path1LogNodeId:
                        row = lmdao.findPathByNodes(cursor, path1LogNodeId, logNodeId)
                        if row:
                            pathId = row[0]
                            timeEvent=datetime.datetime.strptime(logEvent.timeexec, '%Y-%m-%d %H:%M:%S.%f') 
                            timeEventBefore=datetime.datetime.strptime(path1Exectime, '%Y-%m-%d %H:%M:%S.%f') #2017-04-06 15:39:28.890
                            duration=timeEvent-timeEventBefore #datetime.timedelta    
                            desviation = None
                            if row[2] : #if duration_avg desviation = duration normalized (x - AVG)/STD
                                  desviation =  (duration.total_seconds() - row[2])/row[3]                                                                        
                            eventdao.updateLogEventDurationAndPathId(cursor, logEventId, duration.total_seconds(), pathId, desviation)
                            connDbMemory.commit()
                            self.countPathsFound += 1
#                            logger.debug("Update eventLog " + str(logEventId)+" with "+str(pathId))
                        else:
                            logger.debug("Path not found:" + str(path1LogNodeId)+"->"+str(logNodeId))
                                                
                    path1LogNodeId = logNodeId
                    path1Exectime = logEvent.timeexec
#                elif logNodeCategory == lmdao.NODE_CATEGORY_ISSUE:
#                    eventdao.updateLogEventIssueLogNodeId(cursor, logEventId, logNodeId)
#                    connDbMemory.commit()
               
                logThreadCount += 1
                lastLogEventId = logEventId
                finishDate = logEvent.timeexec
                lmdao.updateLogThread(cursor, logThreadId, logThreadCount, finishDate, lastLogEventId, path1LogNodeId, path1Exectime)
                connDbMemory.commit()

        self.setState(th.ThreadState.ENDING)
        connDbMemory.commit()
        connDbData.close()
        
        #Save base db
        db.deleteDbFile(self.readerConfig.dbBasePath)  
        connDbBase=db.connectDb(self.readerConfig.dbBasePath)
        db.copyDbDataSelection(connDbMemory, connDbBase, ['lmp_logPathsT', 'lmp_logNodesT', 'lmp_logThreadsT', 'lmp_logDetailedPathsT'])              
        connDbBase.close()
        
        
        #Save events db
        if self.enableSaveEvents:
            #db.deleteDbFile(self.readerConfig.dbEventsPath)  
            connDbEvents=db.connectDb(self.readerConfig.dbEventsPath)
            db.copyDbDataSelection(connDbMemory, connDbEvents, ['lmp_logEventsT'])                          
            connDbEvents.close()        
        
        connDbMemory.close()                            
                
              
        
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

    cfg.createDefaultConfigfile()
    config=cfg.loadConfig()   

    key = 'device'
    readerConfig = cfg.loadReaderConfig(config, key)
    if readerConfig.enable:
        readerThread = ReaderThread(readerConfig, th.OperationMode.NORMAL)
        readerThread.start() 
    
    
    input("Press key to finish")  
    readerThread.stopRun()
    
    print("BytesReaded = " + str(readerThread.bytesProcessed))
    print("Lines       = " + str(readerThread.loopCount))
    print("Parsed      = " + str(readerThread.recordsProcessed))
    print("PathsFound  = " + str(readerThread.countPathsFound))
    
    print("End module execution") 