# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 18:29:21 2018

@author: abaena
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 20:35:07 2017

@author: abaena
"""

import logging


logger = logging.getLogger(__name__)
import datetime


def createTablesBase(conn):
    """
    Create tables mapper logmapper
    """    
    cursor = conn.cursor()        
      
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_monitor_microservice_dataT
        (
          id INTEGER PRIMARY KEY,
          exectime TEXT,
          fail TEXT,
          memused REAL,
          heapused REAL,
          nonheapused REAL,
          threads INTEGER,
          classes INTEGER,
          sessions INTEGER,
          dsconn INTEGER
        )
    ''') 
         
    conn.commit() 
    cursor.close()
    
def insertMeasure(cursor, queryData):
    cursor.execute(
    """
    INSERT INTO lmp_monitor_microservice_dataT(exectime, 
          memused,
          heapused,
          nonheapused,
          threads,
          classes,
          sessions,
          dsconn
    ) 
    VALUES (?, 
    ?, ?, ?, ?, ?, ?, ?
    );
    """
    , queryData)  
    
def insertMeasureFail(cursor, failmsg):
    cursor.execute(
    """
    INSERT INTO lmp_monitor_microservice_dataT(exectime, fail) 
    VALUES (?, ?);
    """
    , (datetime.datetime.now(), failmsg) )        