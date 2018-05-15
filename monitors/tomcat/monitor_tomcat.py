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

import monitors.tomcat.monitor_tomcat_dao as monitordao


#%%
"""
Global Initialization. cfgants definitions.
"""

logger = logging.getLogger(__name__)

#%%

import logging
import requests
from requests.auth import HTTPBasicAuth
import xml.dom.minidom

requests.packages.urllib3.disable_warnings()
headers = {'Content-type': 'application/json;charset=utf-8', 'Accept-Encoding': 'gzip,deflate'} # 'Accept': 'text/plain' charset=utf-8


def getTomcatMetrics(url, user, password):
    url = url+"/status?XML=true"
    r = requests.get(url, auth=HTTPBasicAuth(user, password), headers=headers, verify=False)
    if r.status_code != 200:
        return("Error: {}".format(r.status_code))
        
    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parseString(r.text)
    status = DOMTree.documentElement
    
    jvm = status.getElementsByTagName("jvm")
    if len(jvm) > 0:
        memory = jvm[0].getElementsByTagName("memory")
        if len(memory) > 0:
            freemem = int(memory[0].getAttribute("free"))
            maxmem = int(memory[0].getAttribute("max"))
#            total = memory[0].getAttribute("total")

   
    connectors = status.getElementsByTagName("connector")   
    for connector in connectors:
        connectorName=connector.getAttribute("name")
        
        if "8080" in connectorName:
        
            threadInfo = connector.getElementsByTagName("threadInfo")
            if len(threadInfo) > 0:
                threads = threadInfo[0].getAttribute("currentThreadCount")
                threadsBusy = threadInfo[0].getAttribute("currentThreadsBusy")
                logger.debug(threadInfo[0].getAttribute("maxThreads"))              
                
            requestInfo = connector.getElementsByTagName("requestInfo")
            if len(requestInfo) > 0:
#                logger.debug(requestInfo[0].getAttribute("maxTime"))
#                logger.debug(requestInfo[0].getAttribute("processingTime"))
#                logger.debug(requestInfo[0].getAttribute("requestCount"))            
#                logger.debug(requestInfo[0].getAttribute("errorCount")) 
                bytesReceived = requestInfo[0].getAttribute("bytesReceived")
                bytesSent = requestInfo[0].getAttribute("bytesSent")
                
            workers = connector.getElementsByTagName("workers")
            if len(workers) > 0:
                workers = workers[0].getElementsByTagName("worker")   
                workerslen = len(workers)
#                for worker in workers:
#                    logger.debug(worker.getAttribute("stage")) 
#                    logger.debug(worker.getAttribute("remoteAddr")) 
#                    logger.debug(worker.getAttribute("currentUri")) 
#                    logger.debug(worker.getAttribute("currentQueryString")) 
#                    logger.debug(worker.getAttribute("requestProcessingTime")) 
#                    logger.debug(worker.getAttribute("requestBytesSent")) 
#                    logger.debug(worker.getAttribute("requestBytesReceived")) 
    
    memused = 1 - freemem/maxmem              
    data = {
            'memused' : memused,
            'threads' : threads,
            'threadsBusy' : threadsBusy,
            'bytesReceived' : bytesReceived,
            'bytesSent' : bytesSent,
            'workers' : workerslen
            } 
    return data 
   

def saveTomcatMetrics(connDbMonitor, data):
    cursor = connDbMonitor.cursor()
    exectime = datetime.datetime.now()
    queryData = [exectime, 
                 data['memused'],
                 data['threads'],
                 data['threadsBusy'],
                 data['bytesSent'],
                 data['bytesSent'],
                 data['workers']
                 ]
    monitordao.insertMeasure(cursor, queryData)
    connDbMonitor.commit()
    return len(queryData)*4
         


class MonitorTomcatThread(th.LogMapperThread):
    
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
            data=getTomcatMetrics(self.monitorConfig.url, self.monitorConfig.user, self.monitorConfig.pwd)
            bytesProcessed=saveTomcatMetrics(connDbMonitor, data)
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
        logger.debug("process")
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
                sender = ds.DataSenderThread(self.name, self.monitorConfig.masterHost, self.monitorConfig.masterPort, lmkey.DATATYPE_MONITOR_TOMCAT, j)
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
    key='tomcat'
    monitorConfig = cfg.loadMonitorConfig(config, key)
    t = MonitorTomcatThread(monitorConfig, th.OperationMode.NORMAL)   
    t.start()
    
    input("Press a key to finish")
    t.stopRun()
    
    #wait thread end
    t.join()
    
    print("loopCount="+str(t.loopCount)+",loopCount="+str(t.recordsProcessed),",bytesProcessed="+str(t.bytesProcessed))
    
    print("End module execution")