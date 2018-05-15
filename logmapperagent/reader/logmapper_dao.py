# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 16:07:09 2018

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

logger = logging.getLogger(__name__)

#
#NODE_CATEGORY_NEW   = 'N'
#NODE_CATEGORY_NONE  = 'I'
#NODE_CATEGORY_ISSUE = 'ISSUE'
#NODE_CATEGORY_NODE  = 'NOD'


def createTablesBase(cursor):
    """
    Create tables reader logmapper
    """    
    logger.debug("createTablesBase")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logNodesT
        (
          id INTEGER PRIMARY KEY,
          key TEXT,
          component TEXT,
          className TEXT,
          method TEXT,
          lineNumber TEXT,
          logLevel TEXT,
          text TEXT,
          category INTEGER NOT NULL, 
          extra TEXT,        
          
          count INTEGER      
               
        )
    ''') 
        
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS index_logNodes_key ON lmp_logNodesT (key);
    ''')  
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logPathsT
        (
          id INTEGER PRIMARY KEY,
          node1_id INTEGER NOT NULL,
          node2_id INTEGER NOT NULL,   
          count INTEGER,
          duration_avg REAL,
          duration_std REAL,
          duration_min REAL,
          duration_max REAL         
        )
    ''')    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logThreadsT
        (
          id INTEGER PRIMARY KEY,
          key TEXT, 
          creation TEXT,
          finish TEXT,
          invalid INTEGER DEFAULT 0,
          count INTEGER,
          lastLogEventId INTEGER,
          path1LogNodeId INTEGER,
          path1Exectime TEXT
        )
    ''') 
         
          
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS index_logThreads_key ON lmp_logThreadsT (key);
    ''') 

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logDetailedPathsT
        (
          id INTEGER PRIMARY KEY,
          node1_id INTEGER NOT NULL,
          node2_id INTEGER NOT NULL,   
          count INTEGER,
          state INTEGER DEFAULT 0,
          path_id INTEGER
        )
    ''') 

    
    
def findLogNodeIdByKey(cursor, key):
    """ 
    ===========================================================================
    Find Id LogNode by key. Return id and count 
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * key (str): key of the node
    **Returns**:
        Tuple: ``(id, count, category)``
    """    
    cursor.execute("SELECT id, count, category FROM lmp_logNodesT WHERE key = ?;", (key, ))
    return cursor.fetchone()
 
    
def insertLogNode(cursor, logEvent):
    """ 
    ===========================================================================
    Insert or create LogNode
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logEvent (LogEvent): object with logEvent data.
    **Returns**:
        None
    """  
    queryData=(logEvent.key, logEvent.component, logEvent.className, logEvent.method, logEvent.lineNumber, logEvent.logLevel, logEvent.text, logEvent.eventCategory.value, 1)
    cursor.execute("INSERT INTO lmp_logNodesT(key, component, className, method, lineNumber, logLevel, text, category, count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", queryData) 
                       
def updateLogNodeCount(cursor, logNodeId, count):
    """ 
    ===========================================================================
    Update count of LogNode
    =========================================================================== 
    If args are invalid return false, and program must exit    
    
    **Args**:
        * cursor: cursor db connection
        * logNodeId (int): Id logNode to update
        * count (int): new count value
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logNodesT SET count = ? WHERE id = ?;", (count, logNodeId) )
    

    
def findLogThreadByKey(cursor, threadKey):
    """ 
    ===========================================================================
    Find LogThread by key 
    =========================================================================== 
    
    **Args**:
        * cursor: cursor db connection
        * key (str): key of the node
    **Returns**:
        Tuple: ``(id, count, lastLogEventId, path1LogNodeId, path1Exectime, creation)``
    """    
    cursor.execute("SELECT id, count, lastLogEventId, path1LogNodeId, path1Exectime, creation FROM lmp_logThreadsT WHERE key = ? AND invalid = 0;", (threadKey, ) )
    return cursor.fetchone()  



def findLogThreadReadyToProcess(cursor, start, end):
    """ 
    ===========================================================================
    Find All LogThread Ready for process in order to search paths
    The threads must be finish
    =========================================================================== 
    
    **Args**:
        * cursor: cursor db connection
    **Returns**:
        [Tuple]: ``(id, )``
    """ 
    if start and end:
        cursor.execute("SELECT id FROM lmp_logThreadsT WHERE creation > ? and finish < ?", (start, end) ) # WHERE invalid = 0
    else:
        cursor.execute("SELECT id FROM lmp_logThreadsT" )
    return cursor.fetchall() 


def setLogThreadInvalid(cursor, threadKey, threadId):
    """ 
    ===========================================================================
    Update LogThread in order to invalid thread
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logNodeId (int): Id logNode to update
        * count (int): new count value
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logThreadsT SET key = ?, invalid = 1 WHERE id = ?;", ("INV_"+threadKey, threadId ) )
    

def insertLogThread(cursor, threadKey, timeexec):
    """ 
    ===========================================================================
    Insert or create LogThread
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logEvent (LogEvent): object with logEvent data.
    **Returns**:
        None
    """     
    data=(threadKey, timeexec, 1)
    cursor.execute("INSERT INTO lmp_logThreadsT(key, creation, count) VALUES (?, ?, ?);", data) 
    
    
def updateLogThread(cursor, logThreadId, logThreadCount, finishDate, lastLogEventId, path1LogNodeId, path1Exectime):
    """ 
    ===========================================================================
    Insert or create LogThread
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logEvent (LogEvent): object with logEvent data.
    **Returns**:
        None
    """        
    queryData = ( logThreadCount, finishDate, lastLogEventId, path1LogNodeId, path1Exectime, logThreadId )
    cursor.execute("UPDATE lmp_logThreadsT SET count = ?, finish = ?, lastLogEventId= ?, path1LogNodeId = ?, path1Exectime = ? WHERE id = ?;", queryData)
    

def updateCategoryLogNodesListSet(cursor, idList, category):   
    """ 
    ===========================================================================
    Update category in logNodes
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * idList ([int]) : list of ids
        * category (str) : new category value
    **Returns**:
        None
    """    
    cursor.executemany("UPDATE lmp_logNodesT SET category = ? WHERE id = ? ;", ((category.value, val) for val in idList)) 


#******************************************************************************
# Mapper Methods
# 
#
#******************************************************************************

    
def findPathByNodes(cursor, node1Id, node2Id):
    """ 
    ===========================================================================
    Find Path by node1Id and node2Id
    =========================================================================== 
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int)
        * node2Id (int)
    **Returns**:
        Tuple: ``(id, count)``
    """     
    cursor.execute("SELECT id, count, duration_avg, duration_std, duration_avg, duration_max FROM lmp_logPathsT WHERE node1_id = ? AND node2_id = ?", (node1Id, node2Id))
    return cursor.fetchone() 


def insertPath(cursor, node1Id, node2Id):
    """ 
    ===========================================================================
    Insert or create Path
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int)
        * node2Id (int)
    **Returns**:
        None
    """     
    cursor.execute(
    """
    INSERT INTO lmp_logPathsT(
    node1_id, 
    node2_id, 
    count) 
    VALUES ( ?, ?, ?)
    """
    , (node1Id, node2Id, 1)
    )
    
def findPathsWithoutStats(cursor):
    """ 
    ===========================================================================
    Find Path without stats
    =========================================================================== 
    
    **Args**:
        * cursor: cursor db connection
    **Returns**:
        Tuple: ``(id, count)``
    """     
    cursor.execute("SELECT id, count FROM lmp_logPathsT WHERE duration_avg IS NULL")
    return cursor.fetchall() 

                   
def updatePathCount(cursor, pathId, count):
    """ 
    ===========================================================================
    Update count of LogNode
    ===========================================================================   
    
    **Args**:
        * cursor: cursor db connection
        * pathId (int): Id to update
        * count (int): new count value
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logPathsT SET count = ? WHERE id = ?", (count, pathId) )

def updatePathStats(cursor, pathId, avg, std, minv, maxv):
    """ 
    ===========================================================================
    Update count of LogNode
    ===========================================================================   
    
    **Args**:
        * cursor: cursor db connection
        * pathId (int): Id to update
        * count (int): new count value
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logPathsT SET duration_avg = ?, duration_std = ?, duration_avg = ?, duration_max = ? WHERE id = ?", (avg, std, minv, maxv, pathId) )
    


def findOnePendingDetailPath(cursor):
    """ 
    ===========================================================================
    Find detailPath pending for process. Only return one record
    =========================================================================== 
    
    **Args**:
        * cursor: cursor db connection
    **Returns**:
        Tuple: ``(id, )``
    """     
    cursor.execute("SELECT id, node1_id, node2_id FROM lmp_logDetailedPathsT WHERE state = 0 LIMIT 1;")  
    return cursor.fetchone()   



def findDetailPathByNodes(cursor, node1Id, node2Id):
    """ 
    ===========================================================================
    Find detailPath pending for process. Only return one record
    =========================================================================== 
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int)
        * node2Id (int)
    **Returns**:
        Tuple: ``(id, )``
    """ 
    cursor.execute(
    """
    SELECT 
    id,
    count
    FROM lmp_logDetailedPathsT 
    WHERE node1_id = ? AND node2_id = ? 
    """
    , (node1Id, node2Id)
    )
    return cursor.fetchone()  

def insertDetailPath(cursor, node1Id, node2Id):
    """ 
    ===========================================================================
    Insert or create LogNode
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int)
        * node2Id (int)
    **Returns**:
        None
    """     
    cursor.execute(
    """
    INSERT INTO lmp_logDetailedPathsT(
    node1_id, 
    node2_id, 
    count) 
    VALUES ( ?, ?, ?)
    """
    , (node1Id, node2Id, 1)
    )

                   
def updateDetailPathCount(cursor, detailedPathId, count):
    """ 
    ===========================================================================
    Update count of LogNode
    ===========================================================================   
    
    **Args**:
        * cursor: cursor db connection
        * detailedPathId (int): Id to update
        * count (int): new count value
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logDetailedPathsT SET count = ? WHERE id = ?", (count, detailedPathId) )
    
    
def countDetailedPathsByNode1(cursor, node1Id):
    """ 
    ===========================================================================
    Count records of DetaildedPaths with node1Id 
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int): Id node1
    **Returns**:
        None
    """     
    cursor.execute("SELECT DISTINCT COUNT(*) FROM lmp_logDetailedPathsT WHERE node1_id = ?", (node1Id,  ))
    return cursor.fetchone() 
    
def countDetailedPathsByNode2(cursor, node2Id):
    """ 
    ===========================================================================
    Count records of DetaildedPaths with node2Id 
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int): Id node1
    **Returns**:
        None
    """     
    cursor.execute("SELECT DISTINCT COUNT(*) FROM lmp_logDetailedPathsT WHERE node2_id = ?", (node2Id,  )) 
    return cursor.fetchone() 
    
    
    
def findOneDetailedPathByNode1(cursor, node1Id):
    """ 
    ===========================================================================
    return one record DetaildedPaths with node1Id 
    ===========================================================================   
    
    **Args**:
        * cursor: cursor db connection
        * node1Id (int): Id node1
    **Returns**:
        None
    """       
    cursor.execute("SELECT id, node1_id, node2_id FROM lmp_logDetailedPathsT WHERE node1_id = ? LIMIT 1", (node1Id,  ))
    return cursor.fetchone() 


def updateDetailedPathListStateProcesed(cursor, idList):   
    """ 
    ===========================================================================
    Update category in logNodes
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * idList ([int]) : list of ids
    **Returns**:
        None
    """  
    cursor.executemany("UPDATE lmp_logDetailedPathsT SET state=1 WHERE id = ? ;", ((val,) for val in idList)) 
    
    
#******************************************************************************
# Master Get Data Methods
# 
#
#****************************************************************************** 
    
#==============================================================================
#tablas 
#==============================================================================
  
#%%
      
def createTablesData(cursor):
    """
    Create tables reader logmapper
    """    
    logger.debug("createTablesLmdata")
    
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_paths_measuresT
        (
          id INTEGER PRIMARY KEY,
          date TEXT NOT NULL,
          path_id INTEGER NOT NULL, 
          count INTEGER,
          duration_avg REAL,
          duration_std REAL,
          duration_max REAL
        )
    ''')
        
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS index_paths_measures_date ON lmp_paths_measuresT (date);
    ''')          
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logeventsT
        (
          id INTEGER PRIMARY KEY,
          date TEXT,
          eventtype INTEGER,
          count INTEGER
        )
    ''') 
        
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS index_logevents_date ON lmp_logeventsT (date);
    ''')        
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logmetricsT
        (
          id INTEGER PRIMARY KEY,
          date TEXT,
          threadsCount INTEGER,
          logCount INTEGER,
          logTraceCount INTEGER,
          logEventsCriticalCount INTEGER,
          logEventsErrorCount INTEGER,
          logEventsWarningCount INTEGER
        )
    ''') 

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS index_logmetrics_date ON lmp_logmetricsT (date);
    ''')


    
def insertPathMeasure(cursor, date, path_id, count, duration_avg, duration_std,duration_max):
    """ 
    ===========================================================================
    Insert or create LogNode
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * 
    **Returns**:
        None
    """  
    cursor.execute("""
    INSERT INTO lmp_paths_measuresT(date, path_id, count, duration_avg, duration_std,duration_max)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (date, path_id, count, duration_avg, duration_std,duration_max) ) 
    
def insertLogEvent(cursor, date, eventtype, count):
    """ 
    ===========================================================================
    Insert or create LogEvent
    User must commit in db in roder to save data.
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * date (datetime): datetime of the period
        * eventtype (int): number indicating type of event
        * count (int): counter of events in the period 
    **Returns**:
        None
    """  
    cursor.execute("""
    INSERT INTO lmp_logeventsT(date, eventtype, count)
    VALUES (?, ?, ?);
    """, (date, eventtype, count) )     
   
def insertLogMetrics(cursor, date, threadsCount, logCount, logTraceCount, 
                     logEventsCriticalCount, logEventsErrorCount, logEventsWarningCount):
    """ 
    ===========================================================================
    Insert or create LogEvent
    User must commit in db in roder to save data.
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * date (datetime): datetime of the period
    **Returns**:
        None
    """  
    cursor.execute("""
    INSERT INTO lmp_logmetricsT(date, 
    threadsCount, logCount, logTraceCount, 
    logEventsCriticalCount, logEventsErrorCount, logEventsWarningCount    
    )
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (date, threadsCount, logCount, logTraceCount, 
        logEventsCriticalCount, logEventsErrorCount, logEventsWarningCount) )
    


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
    
    print("End module execution")     
