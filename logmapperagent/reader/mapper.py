# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 21:07:27 2018

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

import config.config as cfg
import logmappercommon.utils.sqlite_util as db
import logmapperagent.reader.logmapper_dao as lmdao
import logmapperagent.reader.logmapper_events_dao as eventdao
from logmappercommon.definitions.event_categories import LogEventCategories
import logmapperagent.utils.thread_util as th

#%%
"""
Global Initialization. cfgants definitions.
"""

logger = logging.getLogger(__name__)


class MapperThread(th.LogMapperThread):
    """
    Thread for Command Line Interface (CLI)
    """
    
    def __init__(self, readerConfig, operationMode):
        th.LogMapperThread.__init__(self, cfg.THREAD_MAPPER, readerConfig.key, operationMode)    
        self.readerConfig=readerConfig
      
    def process(self):
        #======================================================================
        # Open database connections.
        #   base
        #   events
        #======================================================================   
        if not (
               db.dbFileExist(self.readerConfig.dbBasePath) and
               db.dbFileExist(self.readerConfig.dbEventsPath) 
               ):
           logger.warning("DB Files missing")
           return
        
        connDbBase=db.connectDb(self.readerConfig.dbBasePath)
        connDbEvents=db.connectDb(self.readerConfig.dbEventsPath)
        
        #======================================================================
        # Open memory database connection
        # Load data from file databases
        #======================================================================          
        
        connDbMemory=db.connectDbMemory()
        
        db.copyDbData(connDbBase, connDbMemory)
        #TODO No es necesario cargar todo logEvent
        db.copyDbData(connDbEvents, connDbMemory)               
        connDbBase.close()
        connDbEvents.close()        
        cursor = connDbMemory.cursor()
        
        #======================================================================
        # 
        #======================================================================  
        self.setState(th.ThreadState.PROCESSING)
        
#        now = datetime.datetime.now()
#        start = now - datetime.timedelta(minutes = 20)
#        end = now - datetime.timedelta(minutes = 5)
        start = None
        end = None
        
        rows = lmdao.findLogThreadReadyToProcess(cursor, start, end)
        logger.debug("Threads found:"+str(len(rows)))
        for thread in rows:
            if self._stopRun: return
            processThread(connDbMemory, thread) 
           
        #======================================================================
        # 
        #======================================================================   
        while not self._stopRun:     
            row = lmdao.findOnePendingDetailPath(cursor)
            if not row:
                logger.debug("lmp_logDetailedPaths not found, break")
                break      
            simplifyPaths(connDbMemory, row[0], row[1], row[2])    
            
        #======================================================================
        # Calculate statistics of paths. 
        # Only calc new paths
        #======================================================================   
#        self.setState(MapperState.CALC_STATS)  
#        rows = lmdao.findPathsWithoutStats(cursor)
#        for row in rows:
#            logger.debug("calcPathStats for pathId: "+str(row[0]))
#            stats = report.calcPathStats(cursor, row[0], None, None)
#            if stats:
#                (avg, std, count, minv, maxv) = stats
#                if count > 2:
#                    lmdao.updatePathStats(cursor, row[0], avg, std, minv, maxv)
           
        #======================================================================
        # 
        #======================================================================             
        self.setState(th.ThreadState.ENDING) 
        
        db.deleteDbFile(self.readerConfig.dbBasePath)
        connDbBase=db.connectDb(self.readerConfig.dbBasePath)
        db.copyDbDataSelection(connDbMemory, connDbBase, ['lmp_logPathsT', 'lmp_logNodesT', 'lmp_logThreadsT', 'lmp_logDetailedPathsT'])
        connDbBase.close()
               
        connDbMemory.close()


#%%
    
def processThread(connDb, thread):
    logger.info("processThread+"+str(thread))
    threadId = thread[0]
    cursor = connDb.cursor()
      
    rows = eventdao.findLogEventsByThreadId(cursor, threadId) 
    
    logger.debug("COUNT="+str(len(rows)))
    
    nodeBefore = None
    for row in rows:
        node2=row[1]
        if nodeBefore==None:
            nodeBefore=node2
            continue
        
        node1=nodeBefore
        nodeBefore=node2
        #TODO VERIFICAR SI ESTA BUSQUEDA ES MAR RAPIDA Q BUSCAR EN UN SOLO KEY
        row = lmdao.findDetailPathByNodes(cursor, node1, node2)   
        
        if not row:
            lmdao.insertDetailPath(cursor, node1, node2)
            connDb.commit() 
        else:
            lmdao.updateDetailPathCount(cursor, row[0], row[1]+1)
            connDb.commit()
            
    cursor.close()
            

#%%
def simplifyPaths(connDb, temPathId, node1, node2) :
    logger.info("simplifyPaths+"+str(node1)+","+str(node2))
    cursor = connDb.cursor()
    
    detailedPathList = []
    nodeList = []
    while True:
        logger.debug("UPDATE newPath:"+str(node1)+","+str(node2))
        row = lmdao.countDetailedPathsByNode1(cursor, node2)
        count_start=row[0] 
        
        row = row = lmdao.countDetailedPathsByNode2(cursor, node2)
        count_end=row[0] 
        
        logger.debug("count_start:"+str(count_start)+", count_end:"+str(count_end))
        
        detailedPathList.append(temPathId)
        nodeList.append( node2 )
        
        if count_start == 1 and count_end == 1:
            row = lmdao.findOneDetailedPathByNode1(cursor, node2)   
            if temPathId == row[0]:
                logger.warning("Row found is the same, break:"+str(temPathId))
                break
            if node1 == node2:
                logger.warning("Round path, break:")
                break;
            temPathId=row[0]
            node2=row[2]
            logger.debug("CONTINUA:"+str(temPathId)+", node2:"+str(node2))
        else:
            logger.debug("FINALIZA newPath:"+str(node1)+","+str(node2))
            nodeList.pop()
            break
            
    logger.debug("detailedPathList:"+str(detailedPathList))
    logger.debug("nodeList:"+str(nodeList))
    
    #TODO para actualizar        
    #LISTA CON TODOS LOS ID DEL detailedpathPATH
    #lista con todos los id d enodos    

    lmdao.updateCategoryLogNodesListSet(cursor, nodeList, LogEventCategories.TRACE_NODE)
    lmdao.updateCategoryLogNodesListSet(cursor, [node1, node2], LogEventCategories.TRACE_MAIN_NODE)        
    lmdao.updateDetailedPathListStateProcesed(cursor, detailedPathList)
    connDb.commit()     
    
    #TODO VERIFICAR SI ESTA BUSQUEDA ES MAR RAPIDA Q BUSCAR EN UN SOLO KEY
    row = lmdao.findPathByNodes(cursor, node1, node2)      
    
    if not row:
        lmdao.insertPath(cursor, node1, node2)
    else:
        lmdao.updatePathCount(cursor, row[0], row[1]+1)
        
    connDb.commit() 
    cursor.close()     
    
    
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

    readers = cfg.getReaders(config)
    for readerName in readers:
        readerName = 'device'
        readerConfig = cfg.loadReaderConfig(config, readerName)
        if readerConfig.enable:
            mapperThread = MapperThread(readerConfig, th.OperationMode.NORMAL)
            mapperThread.start() 
    
    print("Wait mapper finish")  
    mapperThread.join()
    
#    print("PathsFound = " + str(mapperThread.countPathsFound))
#    print("output     = " + str(mapperThread.output))
    
    print("End module execution") 