# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 16:46:12 2018

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
import logmapperagent.commands.get as get
import logmapperagent.utils.thread_util as th
import logmapperagent.utils.datasender as ds
import logmappercommon.definitions.logmapperkeys as lmkey

import logmappercommon.utils.postgres_util as psqldb
import monitors.postgres.monitor_postgres_dao as monitordao


#%%
"""
Global Initialization. cfgants definitions.
"""

logger = logging.getLogger(__name__)

#%%


def getPostgresMetrics(host, user, password):
    connDb=psqldb.connectDb("postgres", host, user, password)
    cursor = connDb.cursor()
    conns = psqldb.getDbCountTransactions(cursor)
    locks = psqldb.getDbLocksExclusive(cursor)
    connDb.close()    
    
    data = {
            'conns' : conns,
            'locks' : locks
            } 
    return data    

def savePostgresMetrics(connDbMonitor, data):
    cursor = connDbMonitor.cursor()
    exectime = datetime.datetime.now()
    queryData = [exectime, 
                 data['conns'],
                 data['locks']
                 ]
    monitordao.insertMeasure(cursor, queryData)
    connDbMonitor.commit()
    return len(queryData)*4
         


class MonitorPostgresThread(th.LogMapperThread):
    
    def __init__(self, monitorConfig, operationMode):
        th.LogMapperThread.__init__(self, cfg.THREAD_MONITOR, monitorConfig.key, operationMode)  
        self.monitorConfig = monitorConfig
        self.enableDataSend = self.monitorConfig.enableSendData
        
    def createMonitorDb(self):  
        connDbMonitor=db.connectDb(self.monitorConfig.dbMonitorPath) 
        monitordao.createTablesBase(connDbMonitor)
        connDbMonitor.commit()
        connDbMonitor.close()    
    
    def monitor(self):
        logger.debug("monitor:" + self.monitorConfig.key)
        
        try:
            connDbMonitor=db.connectDb(self.monitorConfig.dbMonitorPath) 
            data=getPostgresMetrics(self.monitorConfig.host, self.monitorConfig.user, self.monitorConfig.pwd)
            bytesProcessed=savePostgresMetrics(connDbMonitor, data)
            connDbMonitor.close() 
            return bytesProcessed
        except Exception as exc:
            logger.exception("Exception in monitor")
            self.fails += 1
            cursor = connDbMonitor.cursor()
            monitordao.insertMeasureFail(cursor, str(exc))  
            connDbMonitor.commit()             
            connDbMonitor.close()  
            return -1        
    
     
    def process(self):
        logger.debug("process2")
        self.createMonitorDb()       
        self.setState(th.ThreadState.PROCESSING)
        while not self._stopRun: 
            self.loopCount += 1
            bytesProcessed = self.monitor()
            if bytesProcessed > 0:
                self.recordsProcessed += 1
                self.bytesProcessed += bytesProcessed
            time.sleep(self.monitorConfig.interval)

            #==================================================================
            # Preprocess data. Summarize data 
            #==================================================================            
            now = datetime.datetime.now() 
            if now > self.nextSaveDataDate and self.enableDataSend:
                self.nextSaveDataDate = lmutil.getNextLogMapperIntervalDate(now)
                start = lmutil.getBeforeMapperIntervalDate(now)
                end = lmutil.getLogMapperIntervalDate(now)
                j = get.getJsonMonitorMeasures(self.monitorConfig, start, end)
                j['lmstats'] = self.getCounters()
                logger.debug("send:"+str(start)+" - "+str(end))
                sender = ds.DataSenderThread(self.name, self.monitorConfig.masterHost, self.monitorConfig.masterPort, lmkey.DATATYPE_MONITOR_POSTGRES, j)
                sender.start()                
            #==================================================================
            # check day change, reset memory database
            #==================================================================  
            if self.currentDate != now.date():
                dayBefore=str(self.currentDate)
                logger.info('Day end. reset data: '+dayBefore)
                self.currentDate = datetime.date.today() 
                
                newFile = self.monitorConfig.dbMonitorPath + "." + dayBefore
                db.copyDbFile(self.monitorConfig.dbMonitorPath, newFile)
                db.deleteDbFile(self.monitorConfig.dbMonitorPath)
                self.createMonitorDb()
            
        self.setState(th.ThreadState.ENDING)        
    

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
    key='postgres'
    monitorConfig = cfg.loadMonitorConfig(config, key)
    t = MonitorPostgresThread(monitorConfig, th.OperationMode.NORMAL)   
    t.start()
    
    input("Press a key to finish")
    t.stopRun()
    
    #wait thread end
    t.join()
    
    print("loopCount="+str(t.loopCount)+",loopCount="+str(t.recordsProcessed),",bytesProcessed="+str(t.bytesProcessed))
    
    print("End module execution")