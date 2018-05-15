# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:43:21 2017

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
import datetime
import json

import numpy as np

import logmapperagent.control.cli as cli
import config.config as cfg
import logmappercommon.utils.sqlite_util as db
import logmappercommon.utils.logmapper_util as lmutil
import logmappercommon.definitions.event_categories as cat
import logmappercommon.definitions.logmapperkeys as lmkey

logger = logging.getLogger(__name__)

class GetCommand(cli.LogMapperCommandDefinition):

    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        if not self.arg1:
            return cli.LogMapperCommandResponse(False, "Invalid option")
       
        if self.arg1 == 'agent': 
            return cli.LogMapperCommandResponse(True, json.dumps(getAgent(config)))

        if self.arg1 == 'readers': 
            return cli.LogMapperCommandResponse(True, json.dumps(getReaders(config))) 
        
        if self.arg1 == 'monitors': 
            return cli.LogMapperCommandResponse(True, json.dumps(getMonitors(config)))         
        
        if self.arg1 == 'logkeys' and len(self.args) == 2: 
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            return cli.LogMapperCommandResponse(True, json.dumps(getLogNodesByCategoryTrace(readerConfig)))        
        
        if self.arg1 == 'paths' and len(self.args) == 2: 
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            return cli.LogMapperCommandResponse(True, json.dumps(getLogPaths(readerConfig))) 
        
        if self.arg1 == 'pathMeasures' and len(self.args) == 4:
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            start = datetime.datetime.strptime(self.args[2], '%Y-%m-%dT%H:%M')
            end = datetime.datetime.strptime(self.args[3], '%Y-%m-%dT%H:%M')
            return cli.LogMapperCommandResponse(True, json.dumps(getJsonPathMeasures(readerConfig, start, end)))  

        if self.arg1 == 'logEventsCount' and len(self.args) == 4:
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            start = datetime.datetime.strptime(self.args[2], '%Y-%m-%dT%H:%M')
            end = datetime.datetime.strptime(self.args[3], '%Y-%m-%dT%H:%M')
            return cli.LogMapperCommandResponse(True, json.dumps(getJsonLogEventsCount(readerConfig, start, end)))  
        
        if self.arg1 == 'logMetrics' and len(self.args) == 4:
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            start = datetime.datetime.strptime(self.args[2], '%Y-%m-%dT%H:%M')
            end = datetime.datetime.strptime(self.args[3], '%Y-%m-%dT%H:%M')
            return cli.LogMapperCommandResponse(True, json.dumps(getJsonLogMetrics(readerConfig, start, end)))   
        
        if self.arg1 == 'logMetricsColnames' and len(self.args) == 2:
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            return cli.LogMapperCommandResponse(True, json.dumps(getJsonLogColnames(readerConfig)))        
        
        if self.arg1 == 'monMeasures' and len(self.args) == 4:
            key = self.args[1]
            monitorConfig = cfg.loadMonitorConfig(config, key)
            start = datetime.datetime.strptime(self.args[2], '%Y-%m-%dT%H:%M')
            end = datetime.datetime.strptime(self.args[3], '%Y-%m-%dT%H:%M')
            return cli.LogMapperCommandResponse(True, json.dumps(getJsonMonitorMeasures(monitorConfig, start, end))) 
        
        if self.arg1 == 'monMeasuresColnames' and len(self.args) == 2:
            key = self.args[1]
            monitorConfig = cfg.loadMonitorConfig(config, key)
            return cli.LogMapperCommandResponse(True, json.dumps(getJsonMonitorColnames(monitorConfig)))        

        
        if self.arg1 == 'logRecords' and len(self.args) == 4:
            key = self.args[1]
            readerConfig = cfg.loadReaderConfig(config, key)
            start = datetime.datetime.strptime(self.args[2], '%Y-%m-%dT%H:%M')
            end = datetime.datetime.strptime(self.args[3], '%Y-%m-%dT%H:%M')
            return cli.LogMapperCommandResponse(True, json.dumps(getLogEventsWithRemoteCall(readerConfig, start, end)))
			
        if self.arg1 == 'logkeysEvents' and len(self.args) == 3: 
            category = cat.LogEventCategories[self.args[1]]
            key = self.args[2]
            readerConfig = cfg.loadReaderConfig(config, key)
            return cli.LogMapperCommandResponse(True, json.dumps(getLogNodesByCategory(readerConfig, category)))       

        
        return cli.LogMapperCommandResponse(False, "Invalid option")


#%%


def getAgent(config):
    """
    Get Agent and host data
    """
    logger.info('getAgent')
    agentKey = config.get(cfg.SECTION_LOGMAPPER, cfg.PROP_AGENTKEY)
    agentIp = config.get(cfg.SECTION_LOGMAPPER, cfg.PROP_AGENTIP)
    agentPort = config.get(cfg.SECTION_LOGMAPPER, cfg.PROP_AGENTPORT)
    host = config.get(cfg.SECTION_GENERAL, cfg.PROP_HOSTNAME)
    
    data = {'agentKey' : agentKey, 'agentIp' : agentIp, 
            'agentPort' : agentPort,'host' : host}
    return data

def getReaders(config):
    """
    Get Readers and Component Data
    """ 
    logger.info('getReaders')
    readersList = []
    for reader in cfg.getReaders(config):
        readerConfig = cfg.loadReaderConfig(config, reader)
        r = {'readerKey' : readerConfig.key, 
             'component' : readerConfig.component,
             'host' : readerConfig.hostname,
             'enable' : readerConfig.enable,
             'sourceFilePath' : readerConfig.sourcefilepath,
             'parserModuleName' : readerConfig.moduleName,
             'parserClassName' : readerConfig.className
             }
        readersList.append(r)
        
    data = { 'readers' : readersList }       
    return data

def getMonitors(config):
    """
    Get Readers and Component Data
    """ 
    logger.info('getMonitors')
    monitorList = []
    for key in cfg.getMonitors(config):
        monitorConfig = cfg.loadMonitorConfig(config, key)
        r = {'monitorKey' : monitorConfig.key, 
             'components' : monitorConfig.components,
             'host' : monitorConfig.hostname,
             'type' : monitorConfig.type,
             'enable' : monitorConfig.enable,
             'interval' : monitorConfig.interval
             }
        monitorList.append(r)
        
    data = { 'monitors' : monitorList }       
    return data


def getLogNodesByCategoryTrace(readerConfig):
    """
    Get logNodes
    """  
    logger.info('getLogNodesByCategory')
    connDbBase=db.connectDbOnlyRead(readerConfig.dbBasePath)
    cursor = connDbBase.cursor()
    
    cat1 = cat.LogEventCategories.TRACE_MAIN_NODE

    cursor.execute(
    """
    SELECT 
    id, replace( key, '>>', '' ) as key, 
	component, className, method, lineNumber, logLevel, 
    replace( text, '>>', '' ) as text, 
    category
    FROM lmp_logNodesT 
    WHERE
    category = ?
    """, (cat1.value, )
    )   
    rows = cursor.fetchall() 
    
    data = { 'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname,
            'logItems' : rows } 

    connDbBase.close()
    return data

def getLogNodesByCategory(readerConfig, category):
    """
    Get logNodes
    """  
    logger.info('getLogNodesByCategory:'+str(category))
    connDbBase=db.connectDbOnlyRead(readerConfig.dbBasePath)
    cursor = connDbBase.cursor()
      
  
    cursor.execute(
    """
    SELECT 
    id, key, component, className, method, lineNumber, logLevel, text, category
    FROM lmp_logNodesT 
    WHERE
    category = ?   
    """, (category.value, )
    )   
    rows = cursor.fetchall() 
    
    #agrega una columna con el key+el id
#    rows2 = list(map(lambda row: row + ( (readerKey+'_'+str(row[0])), ), rows))
    #elimina la primera columna
#    rows3 = list(map(lambda row: row[1:], rows2))
    
    data = { 'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname, 
            'logNodes' : rows } 

    connDbBase.close()
    return data

def getLogPaths(readerConfig):
    """
    Get paths
    """   
    logger.info('getLogPaths')
    connDbBase=db.connectDbOnlyRead(readerConfig.dbBasePath)    
    cursor = connDbBase.cursor()      
    
    cursor.execute(
    """
    SELECT  id, node1_id, node2_id
    FROM lmp_logPathsT  
    """
    )   
    rows = cursor.fetchall() 
    
    #agrega una columna con el key+el id
#    rows2 = list(map(lambda row: row + ( (readerKey+'_'+str(row[0])), (readerKey+'_'+str(row[1])), (readerKey+'_'+str(row[2])) ), rows))
    #elimina la primeras 2 columnas
#    rows3 = list(map(lambda row: row[3:], rows2))    
    
    data = { 'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname,  
            'logPaths' : rows } 

    connDbBase.close()
    return data

#%%
    
def getPathMeasures(cursor, start, end):
    logger.info('getPathMeasures: '+str(start)+" - "+str(end))
    measures = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)
        rows = getPathsInPeriod(cursor, start, endLoop)        
        for row in rows:
            pathId=row[0]
            stats = calcPathStats(cursor, pathId, start, endLoop)
            if stats:
                stats2 = ( str(start), str(pathId)) + stats
                measures.append(stats2)           
        start = endLoop    
    return measures
    
    
def getJsonPathMeasures(readerConfig, start, end):
    """
    Get paths measurements
    """   
    logger.info('getJsonPathMeasures: '+str(start)+" - "+str(end))

    connDbData=db.connectDbOnlyRead(readerConfig.dbDataPath)
    cursor = connDbData.cursor()
    cursor.execute("SELECT * from lmp_paths_measuresT WHERE date BETWEEN ? AND ?", (start, end))
    measures = cursor.fetchall()
    connDbData.close() 
           
    
    data = { 'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname, 
            'pathMeasures' : measures }
    return data

def getLogEventsCount(cursor, start, end):
    """
    Get event count 
    """
    logger.info('getLogEventsCount: '+str(start)+" - "+str(end))    
                        
    counters = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)      
        for category in cat.getValuesLogEventCategories(): 
            cursor.execute("""
            SELECT count(*)
            FROM lmp_logEventsT 
            WHERE category=?
            AND exectime  BETWEEN ? AND ?
            """, (category.value, start, endLoop))
            row = cursor.fetchone() 
            if row[0] > 0:
                counters.append( ( str(start), category.name, category.value, row[0] ) )      
        start = endLoop        
    
    return counters


def getJsonLogEventsCount(readerConfig, start, end):
    """
    Get event count 
    """
    logger.info('getJsonLogEventsCount: '+str(start)+" - "+str(end))
    
    connDbData=db.connectDbOnlyRead(readerConfig.dbDataPath)
    cursor = connDbData.cursor()
    cursor.execute("SELECT * from lmp_logeventsT WHERE date BETWEEN ? AND ?", (start, end))
    counters = cursor.fetchall()
    connDbData.close()                       
    
    data = { 'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname,
            'datatype' : lmkey.DATATYPE_LOG_EVENTS,
            'logEventsCount' : counters }

    return data



def getLogMetrics(cursor, start, end):
    """
    Get event count 
    """
    logger.info('getLogMetrics: '+str(start)+" - "+str(end)) 
        
    metrics = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)  
        
        threadsCount = 0
        logCount = 0
        logTraceCount = 0 
        logEventsCriticalCount = 0
        logEventsErrorCount = 0 
        logEventsWarningCount = 0

        cursor.execute("""
        SELECT count(*)
        FROM lmp_logThreadsT 
        WHERE creation  BETWEEN ? AND ?
        """, (start, endLoop))
        row = cursor.fetchone()        
        threadsCount = row[0]
        
        cursor.execute("""
        SELECT count(*)
        FROM lmp_logEventsT 
        WHERE exectime  BETWEEN ? AND ?
        """, (start, endLoop)) 
        row = cursor.fetchone()
        logCount = row[0]
        
        cursor.execute("""
        SELECT count(*)
        FROM lmp_logEventsT 
        WHERE exectime  BETWEEN ? AND ?
        AND category BETWEEN ? AND ?
        """, (start, endLoop, cat.EV_TRACE_MIN, cat.EV_TRACE_MAX))
        row = cursor.fetchone() 
        logTraceCount = row[0]        
            

        cursor.execute("""
        SELECT count(*)
        FROM lmp_logEventsT 
        WHERE exectime  BETWEEN ? AND ?
        AND category BETWEEN ? AND ?
        """, (start, endLoop, cat.EV_CRIT_MIN, cat.EV_CRIT_MAX))
        row = cursor.fetchone() 
        logEventsCriticalCount = row[0]
        
        cursor.execute("""
        SELECT count(*)
        FROM lmp_logEventsT 
        WHERE exectime  BETWEEN ? AND ?
        AND category BETWEEN ? AND ?
        """, (start, endLoop, cat.EV_ERR_MAX, cat.EV_ERR_MAX))
        row = cursor.fetchone() 
        logEventsErrorCount = row[0]

        cursor.execute("""
        SELECT count(*)
        FROM lmp_logEventsT 
        WHERE exectime  BETWEEN ? AND ?
        AND category BETWEEN ? AND ?
        """, (start, endLoop, cat.EV_WARN_MIN, cat.EV_WARN_MAX))
        row = cursor.fetchone() 
        logEventsWarningCount = row[0]
        
        m = ( str(start), threadsCount, logCount, logTraceCount, 
             logEventsCriticalCount, logEventsErrorCount, logEventsWarningCount)
        metrics.append(m) 
                
        start = endLoop        
   
    return metrics

def getJsonLogMetrics(readerConfig, start, end):
    """
    Get event count 
    """
    logger.info('getJsonLogMetrics: '+str(start)+" - "+str(end))
    
    connDbData=db.connectDbOnlyRead(readerConfig.dbDataPath)
    cursor = connDbData.cursor()
    cursor.execute("SELECT * from lmp_logmetricsT WHERE date BETWEEN ? AND ?", (start, end))
    metrics = cursor.fetchall()
    connDbData.close()   
        
    data = {'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname,
            'datatype' : lmkey.DATATYPE_LOG_METRICS,
            'metrics' : metrics }   
    return data


def formatColnames(colnames, offset):
    colnames2 = []
    count = offset
    for col in colnames:
        colnames2.append({'idx': count, "name" : col})
        count += 1 
    return colnames2

def getJsonLogColnames(readerConfig):
    """
    Get event count 
    """
    logger.info('getJsonLogColnames: ')
    
    connDbData=db.connectDbOnlyRead(readerConfig.dbDataPath)
    cursor = connDbData.cursor()
    cursor.execute("SELECT * from lmp_logmetricsT LIMIT 1")
    colnames = formatColnames(list(map(lambda x: x[0], cursor.description)), 0)
    colnames = colnames[2:] # drop colums 1 y 2: id and date
    
    connDbData.close()   
        
    data = {'readerKey' : readerConfig.key,
            'component' : readerConfig.component,
            'host' : readerConfig.hostname,
            'datatype' : lmkey.DATATYPE_LOG_METRICS,
            'colnames' : colnames}   
    return data


def getJsonMonitorMeasures(monitorConfig, start, end):  
    """
    Get paths
    """
    logger.info('getJsonMonitorMeasures: '+str(start)+" - "+str(end))
   
    if monitorConfig.type == cfg.MONITOR_TYPE_HOST:
        measures = getMonitorHostMeasures(monitorConfig, start, end) 
        datatype = lmkey.DATATYPE_MONITOR_HOST
        sourcetype = lmkey.SOURCE_TYPE_HOST
    elif monitorConfig.type == cfg.MONITOR_TYPE_SPRINGMICROSERVICE:
        measures = getMonitorMicroserviceMeasures(monitorConfig, start, end)
        datatype = lmkey.DATATYPE_MONITOR_MICROSERVICE
        sourcetype = lmkey.SOURCE_TYPE_SPRINGMICROSERVICE
    elif monitorConfig.type == cfg.MONITOR_TYPE_TOMCAT:
        measures = getMonitorTomcatMeasures(monitorConfig, start, end)
        datatype = lmkey.DATATYPE_MONITOR_TOMCAT
        sourcetype = lmkey.SOURCE_TYPE_TOMCAT
    elif monitorConfig.type == cfg.MONITOR_TYPE_POSTGRES:
        measures = getMonitorPostgresMeasures(monitorConfig, start, end) 
        datatype = lmkey.DATATYPE_MONITOR_POSTGRES
        sourcetype = lmkey.SOURCE_TYPE_POSTGRES
       
    data = { 
            'monitorKey' : monitorConfig.key,
            'datatype' : datatype,
            'sourcetype' : sourcetype,
            'measures' : measures
            }
    return data

def getJsonMonitorColnames(monitorConfig):  
    """
    Get paths
    """
    logger.info('getJsonMonitorColnames: ')
   
    if monitorConfig.type == cfg.MONITOR_TYPE_HOST:
        colnames = getMonitorHostColnames(monitorConfig) 
        datatype = lmkey.DATATYPE_MONITOR_HOST
    elif monitorConfig.type == cfg.MONITOR_TYPE_SPRINGMICROSERVICE:
        colnames = getMonitorMicroserviceColnames(monitorConfig)
        datatype = lmkey.DATATYPE_MONITOR_MICROSERVICE
    elif monitorConfig.type == cfg.MONITOR_TYPE_TOMCAT:
        colnames= getMonitorTomcatColnames(monitorConfig)
        datatype = lmkey.DATATYPE_MONITOR_TOMCAT
    elif monitorConfig.type == cfg.MONITOR_TYPE_POSTGRES:
        colnames = getMonitorPostgresColnames(monitorConfig) 
        datatype = lmkey.DATATYPE_MONITOR_POSTGRES
       
    
    data = { 
            'monitorKey' : monitorConfig.key,
            'datatype' : datatype,
            'colnames' : colnames
            }
    return data


def getMonitorHostMeasures(monitorConfig, start, end):  
    """
    Get paths
    """
    logger.info('getMonitorHostMeasures: '+str(start)+" - "+str(end))
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
        
    measures = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)      
        cursor.execute(
        """
           SELECT MAX(cpu), max(cpu_user), MAX(cpu_sys), MIN(cpu_idle), 
           MAX(mem), MAX(swap), MAX(diskusage), MAX(pids), MAX(cnxs), MAX(users),
           MAX(disk_io_rate_w), MAX(disk_io_rate_r), 
           MAX(net_io_rate_r), MAX(net_io_rate_s),
           MAX(openfiles), max(openfiles_rate),
           SUM(net_err_rate_in), SUM(net_err_rate_out),
           SUM(net_drop_rate_in), SUM(net_drop_rate_out)                  
           FROM lmp_monitor_host_dataT 
           WHERE exectime  BETWEEN ? AND ?
        """, (start, endLoop))
        measure = cursor.fetchone()          
        if measure[0]:
            measures.append( (str(start), ) + measure )           
        start = endLoop        
    connDbMonitor.close()
    return measures

def getMonitorHostColnames(monitorConfig):  
    """
    Get paths
    """
    logger.info('getMonitorHostColnames:')
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()     
    cursor.execute(
    """
       SELECT MAX(cpu), max(cpu_user), MAX(cpu_sys), MIN(cpu_idle), 
       MAX(mem), MAX(swap), MAX(diskusage), MAX(pids), MAX(cnxs), MAX(users),
       MAX(disk_io_rate_w), MAX(disk_io_rate_r), 
       MAX(net_io_rate_r), MAX(net_io_rate_s),
       MAX(openfiles), max(openfiles_rate),
       SUM(net_err_rate_in), SUM(net_err_rate_out),
       SUM(net_drop_rate_in), SUM(net_drop_rate_out)                  
       FROM lmp_monitor_host_dataT 
       LIMIT 1
    """)  
    colnames = formatColnames(list(map(lambda x: x[0], cursor.description)), 1)                      
    connDbMonitor.close()
    return colnames

def getMonitorMicroserviceMeasures(monitorConfig, start, end):  
    """
    Get paths
    """
    logger.info('getMonitorMicroserviceMeasures: '+str(start)+" - "+str(end))
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
        
    measures = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)      
        cursor.execute(
        """
           SELECT MAX(memused), MAX(heapused), MAX(nonheapused), 
           MAX(threads), MAX(classes), MAX(sessions), MAX(dsconn),
           COUNT(fail)                 
           FROM lmp_monitor_microservice_dataT 
           WHERE exectime  BETWEEN ? AND ?
        """, (start, endLoop))
        measure = cursor.fetchone()       
        if measure[0]:
            measures.append( (str(start), ) + measure )           
        start = endLoop        
    connDbMonitor.close()
    return measures

def getMonitorMicroserviceColnames(monitorConfig):  
    """
    Get paths
    """
    logger.info('getMonitorMicroserviceColnames:')
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
             
    cursor.execute(
    """
       SELECT MAX(memused), MAX(heapused), MAX(nonheapused), 
       MAX(threads), MAX(classes), MAX(sessions), MAX(dsconn),
       COUNT(fail)                 
       FROM lmp_monitor_microservice_dataT 
       LIMIT 1
    """)
    colnames = formatColnames(list(map(lambda x: x[0], cursor.description)), 1)              
    connDbMonitor.close()
    return colnames

def getMonitorPostgresMeasures(monitorConfig, start, end):  
    """
    Get paths
    """
    logger.info('getMonitorPostgresMeasures: '+str(start)+" - "+str(end))
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
        
    measures = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)      
        cursor.execute(
        """
           SELECT MAX(conns), MAX(locks), 
           COUNT(fail)                 
           FROM lmp_monitor_postgres_dataT 
           WHERE exectime  BETWEEN ? AND ?
        """, (start, endLoop))
        measure = cursor.fetchone()         
        if measure[0]:
            measures.append( (str(start), ) + measure )           
        start = endLoop        
    connDbMonitor.close()
    return measures

def getMonitorPostgresColnames(monitorConfig):  
    """
    Get paths
    """
    logger.info('getMonitorPostgresColnames: ')
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
             
    cursor.execute(
    """
       SELECT MAX(conns), MAX(locks), 
       COUNT(fail)                 
       FROM lmp_monitor_postgres_dataT 
       LIMIT 1
    """)
    colnames = formatColnames(list(map(lambda x: x[0], cursor.description)), 1)             
    connDbMonitor.close()
    return colnames

def getMonitorTomcatMeasures(monitorConfig, start, end):  
    """
    Get paths
    """
    logger.info('getMonitorTomcatMeasures: '+str(start)+" - "+str(end))
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
        
    measures = []
    while start < end: 
        endLoop = start + datetime.timedelta(minutes = lmutil.PERIOD)      
        cursor.execute(
        """
           SELECT 
           MAX(memused), MAX(threads), MAX(threadsBusy), MAX(workers),
           COUNT(fail)                 
           FROM lmp_monitor_tomcat_dataT 
           WHERE exectime  BETWEEN ? AND ?
        """, (start, endLoop))
        measure = cursor.fetchone()         
        if measure[0]:
            measures.append( (str(start), ) + measure )           
        start = endLoop        
    connDbMonitor.close()
    return measures

def getMonitorTomcatColnames(monitorConfig):  
    """
    Get paths
    """
    logger.info('getMonitorTomcatColnames:')
    connDbMonitor=db.connectDbOnlyRead(monitorConfig.dbMonitorPath)     
    cursor = connDbMonitor.cursor()
             
    cursor.execute(
    """
       SELECT 
       MAX(memused), MAX(threads), MAX(threadsBusy), MAX(workers),
       COUNT(fail)                 
       FROM lmp_monitor_tomcat_dataT 
       LIMIT 1
    """) 
    colnames = formatColnames(list(map(lambda x: x[0], cursor.description)), 1)              
    connDbMonitor.close()
    return colnames



def getLogEventsWithRemoteCall(readerConfig, start, end):
    """
    Get event count 
    """
    logger.info('getLogEventsWithRemoteCall: '+str(start)+" - "+str(end))
    
    connDbEvents=db.connectDbOnlyRead(readerConfig.dbEventsPath)
    cursor = connDbEvents.cursor()

    cursor.execute("""
    SELECT exectime, logNode_id, remoteCallKey, userKey
    FROM lmp_logEventsT 
    WHERE remoteCallKey IS NOT NULL AND path_id IS NOT NULL
    AND exectime  BETWEEN ? AND ?
    """, (start, end))  
    rows = cursor.fetchall()      
    
    data = { 'readerKey' : readerConfig.key, 
            'component' : readerConfig.component,
            'host' : readerConfig.hostname,            
            'logRecords' : rows }
    cursor.close()
    connDbEvents.close()
    return data      
  
 
#%%

def getPathsInPeriod(cursor, start, end):
#    logger.info("getPathsInPeriod:"+str(start))
    
    cursor.execute("""
                   SELECT path_id, count(*) 
                   FROM lmp_logEventsT 
                   WHERE lmp_logEventsT.path_id IS NOT NULL 
                   AND exectime  BETWEEN ? AND ?
                   GROUP BY path_id
                   """, (start, end)) 
    return cursor.fetchall()    



def calcPathStats(cursor, pathId, start, end) :
#    logger.debug("calcPathStats+"+str(pathId))  
    
    if start and end:    
        cursor.execute("""
                       SELECT duration
                       FROM lmp_logEventsT 
                       WHERE path_id=?
                       AND exectime  BETWEEN ? AND ?
                       """, (pathId, start, end))
    else:
        cursor.execute("""
                       SELECT duration
                       FROM lmp_logEventsT 
                       WHERE path_id=?
                       """, (pathId, ))
        
    rows = cursor.fetchall()

    
    if rows:
        mat=np.matrix(rows)
    
        durationList=mat[:,0].tolist()       
        avg=np.mean(durationList)
        std=np.std(durationList)
        count=len(durationList)
        maxv=np.max(durationList)
        
        return (count, avg, std, maxv)
        
    else:
        logger.warning("Fallo calcPathStats !!!!!!!!")
        
          
  


   
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    cfg.createDefaultConfigfile()
    config=cfg.loadConfig()
    
    commandDefinition = GetCommand("get", "g", "Help")
    
    daterangestr = "2018-04-12T10:00 2018-04-12T11:00"
    
#    commandDefinition.parseArgs("get agent")
#    commandDefinition.parseArgs("get readers") 
    commandDefinition.parseArgs("get monitors")
#    commandDefinition.parseArgs("get logkeys device")    
#    commandDefinition.parseArgs("get paths device") 
#    commandDefinition.parseArgs("get pathMeasures device "+daterangestr) 
#    commandDefinition.parseArgs("get logEventsCount device "+daterangestr) 
#    commandDefinition.parseArgs("get logMetrics device "+daterangestr) 
    
#    commandDefinition.parseArgs("get monMeasures host "+daterangestr)   
#    commandDefinition.parseArgs("get monMeasures microservice-device "+daterangestr)
#    commandDefinition.parseArgs("get monMeasures tomcat "+daterangestr)
#    commandDefinition.parseArgs("get monMeasures postgres "+daterangestr)
       
#    commandDefinition.parseArgs("get logMetricsColnames device")
#    commandDefinition.parseArgs("get monMeasuresColnames host")
#    commandDefinition.parseArgs("get monMeasuresColnames microservice-device")
#    commandDefinition.parseArgs("get monMeasuresColnames tomcat")
#    commandDefinition.parseArgs("get monMeasuresColnames postgres")
           
#    commandDefinition.parseArgs("get logRecords device "+daterangestr)
#    commandDefinition.parseArgs("get logkeysEvents ERROR device")     
        
    response = commandDefinition.execute(config)
    print(str(response))
    
    print("End module execution")