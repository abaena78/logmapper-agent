# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 16:07:31 2018

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

import logmappercommon.definitions.event_categories as evcat

logger = logging.getLogger(__name__)
    
def createTablesEvents(cursor):
    """
    Create tables reader logmapper
    """    
    logger.debug("createTablesEvents")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_logEventsT
        (
          id INTEGER PRIMARY KEY,
          thread_id INTEGER, 
          logNode_id INTEGER,
          detail TEXT,
          exectime TEXT,  
          remoteCallKey TEXT,
          userKey TEXT,
          tenantKey TEXT,
          executionState TEXT,
          category INTEGER,

          event_before_id INTEGER,
          path_id INTEGER,
          issue_logNode_id INTEGER,
          duration REAL,
          desviation REAL
        )
    ''')
          
    
def truncateTableLogEvents(cursor, currentId=None):     
    cursor.execute("DROP TABLE IF EXISTS lmp_logEventsT")
    createTablesEvents(cursor)
    if currentId:
        cursor.execute("INSERT INTO lmp_logEventsT(id) VALUES (?);", (currentId, ))   
#    cursor.execute("DELETE FROM lmp_logEventsT;") 
    
    
def insertLogEvent(cursor, logThreadId, logNodeId, timeexec, remoteCallKey, userKey, lastLogEventId, category):
    """ 
    ===========================================================================
    Insert or create LogEvent
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logEvent (LogEvent): object with logEvent data.
    **Returns**:
        None
    """    
    queryData=( logThreadId, logNodeId, timeexec, remoteCallKey, userKey, lastLogEventId, category )
    cursor.execute("INSERT INTO lmp_logEventsT(thread_id, logNode_id, exectime, remoteCallKey, userKey, event_before_id, category) VALUES (?, ?, ?, ?, ?, ?, ?);", queryData) 
    
    
    
def updateLogEventDurationAndPathId(cursor, logEventId, duration, pathId, desviation):
    """ 
    ===========================================================================
    Update duration and pathId of LogEvent
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logEventId (int):Id LogEvent to update
        * duration (real): duration in seconds
        * pathId (int): id path
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logEventsT SET duration = ?, path_id = ?, desviation = ? WHERE id = ?", (duration, pathId, desviation, logEventId))


def updateLogEventIssueLogNodeId(cursor, logEventId, issueLogEventId):
    """ 
    ===========================================================================
    Update issueLogEventId of LogEvent. 
    This is when logNode category is EVE
    ===========================================================================    
    
    **Args**:
        * cursor: cursor db connection
        * logEventId (int):Id LogEvent to update
        * logNodeEventId (int): id logNode
    **Returns**:
        None
    """    
    cursor.execute("UPDATE lmp_logEventsT SET issue_logNode_id = ? WHERE id = ?", (issueLogEventId, logEventId))


#==================================================================================================
# Mapper methods    
#==================================================================================================
    
    
    
def findLogEventsByThreadId(cursor, threadId):   
    """ 
    ===========================================================================
    Find logEvents By Thread order ASC
    ===========================================================================
    LogEvents not incude category EVE    
    
    **Args**:
        * cursor: cursor db connection
        * threadId (int) Id Thread
    **Returns**:
        None
    """ 

    cursor.execute(
    """
    SELECT 
    lmp_logEventsT.id,
    lmp_logEventsT.logNode_id
    FROM lmp_logEventsT 
	 INNER JOIN lmp_logNodesT ON lmp_logNodesT.id = lmp_logEventsT.logNode_id
    WHERE lmp_logNodesT.category <= ?  AND lmp_logEventsT.thread_id = ?
    ORDER BY lmp_logEventsT.id ASC
    """
    , (evcat.EV_TRACE_MAX, threadId )
    )    
    return cursor.fetchall()  


def findLastLogEventId(cursor):     
    cursor.execute("SELECT id FROM lmp_logEventsT ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        return row[0] 
    return 0




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