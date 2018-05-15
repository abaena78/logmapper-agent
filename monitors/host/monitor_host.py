# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 17:08:40 2018

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
import datetime
import time
import psutil
import platform
import subprocess

import config.config as cfg
import logmappercommon.utils.sqlite_util as db
import logmapperagent.utils.thread_util as th
import logmapperagent.utils.datasender as ds
import logmappercommon.utils.logmapper_util as lmutil
import logmapperagent.commands.get as get
import monitors.host.monitor_host_dao as monitordao
import logmappercommon.definitions.logmapperkeys as lmkey



logger = logging.getLogger(__name__)


GET_OPENFILES_MOD_LOOP_COUNT = 20


    
def getOpenFiles():
    p=subprocess.Popen(["lsof", "-nf", "--"], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    return len(output.splitlines())    
                    
      
def saveMonitorData(connDbMonitor, loopCount=0):
    """ 
    ===========================================================================
    Monitor Task
    ===========================================================================   
    
    **Args**:
        host (str): name of the host
    **Returns**:
        None
    """

    cursor = connDbMonitor.cursor()       
    
    osName = os.name+" "+platform.system()+" "+platform.release()

    #==========================================================================
    #
    #==========================================================================      
    
    
    #==========================================================================
    #
    #==========================================================================     
    
    exectime = datetime.datetime.now()
    cpu = psutil.cpu_percent()
    cputimes = psutil.cpu_times_percent() 
    cpu_user =cputimes[0]
    cpu_sys =cputimes[1]
    cpu_idle =cputimes[2] 
    
    mem = psutil.virtual_memory()[2]
    swap =  psutil.swap_memory()[3]
    diskusage = psutil.disk_usage(os.getcwd())[3]
    pids = len(psutil.pids())
    cnxs = len(psutil.net_connections())
    users = len(psutil.users())
    
    disk_io_count = psutil.disk_io_counters()
    disk_io_count_w = disk_io_count[3]
    disk_io_count_r = disk_io_count[2]
    
    net_io_count = psutil.net_io_counters()
    net_io_count_s = net_io_count[0]
    net_io_count_r = net_io_count[1]
    net_err_in = net_io_count[4]
    net_err_out = net_io_count[5]
    net_drop_in = net_io_count[6]
    net_drop_out = net_io_count[7]
    
    
    if loopCount % GET_OPENFILES_MOD_LOOP_COUNT == 0:   
        if 'Linux' in osName:
            openfiles = getOpenFiles()
        else:
            openfiles = None
        
    
    
#    psutil.cpu_times_percent() 
#    scputimes(user=4.4, system=2.1, idle=93.0, interrupt=0.4, dpc=0.1)
#    
#    psutil.swap_memory()
#    sswap(total=19587432448, used=8541921280, free=11045511168, percent=43.6, sin=0, sout=0)    
    
    
    #==========================================================================
    #
    #==========================================================================      
    
    disk_io_rate_w = None
    disk_io_rate_r = None
    net_io_rate_s = None
    net_io_rate_r = None
    
    net_err_rate_in = None
    net_err_rate_out = None
    net_drop_rate_in = None
    net_drop_rate_out = None
    
    openfiles_rate = None
    
    cursor.execute("SELECT exectime, disk_io_count_w, disk_io_count_r, net_io_count_s, net_io_count_r, net_err_in, net_err_out, net_drop_in, net_drop_out, openfiles FROM lmp_monitor_host_dataT ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()    
    
    if row:
        timebefore=datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f') 
        duration=exectime-timebefore #datetime.timedelta    
        if duration.days < 1:
            disk_io_rate_w = ((disk_io_count_w - row[1])/duration.seconds)/1000
            disk_io_rate_r = ((disk_io_count_r - row[2])/duration.seconds)/1000
            net_io_rate_s = ((net_io_count_s - row[3])/duration.seconds)/1000
            net_io_rate_r = ((net_io_count_r - row[4])/duration.seconds)/1000
            
            net_err_rate_in = ((net_err_in - row[5])/duration.seconds)
            net_err_rate_out = ((net_err_out - row[6])/duration.seconds)
            net_drop_rate_in = ((net_drop_in - row[7])/duration.seconds)
            net_drop_rate_out = ((net_drop_out - row[8])/duration.seconds)
            
            if openfiles:
                openfiles_rate = ((openfiles - row[9])/duration.seconds)
            
    
    queryData=[exectime, 
               cpu, cpu_user, cpu_sys, cpu_idle,
               mem, swap, diskusage, pids, cnxs, users, 
               disk_io_count_w, disk_io_count_r, net_io_count_s, net_io_count_r, 
               openfiles,
               net_err_in, net_err_out, net_drop_in, net_drop_out,
               disk_io_rate_w, disk_io_rate_r, net_io_rate_s, net_io_rate_r,
               net_err_rate_in, net_err_rate_out, net_drop_rate_in, net_drop_rate_out,
               openfiles_rate
               ]
    
    monitordao.insertMeasure(cursor, queryData)
    connDbMonitor.commit()
    return len(queryData)*4


class MonitorHostThread(th.LogMapperThread):
    
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
            bytesProcessed=saveMonitorData(connDbMonitor)
            connDbMonitor.close() 
            return bytesProcessed
        except Exception as exc:
            logger.exception("Exception in monitor")
            self.fails += 1
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
                sender = ds.DataSenderThread(self.name, self.monitorConfig.masterHost, self.monitorConfig.masterPort, lmkey.DATATYPE_MONITOR_HOST, j)
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
    key='host'
    monitorConfig = cfg.loadMonitorConfig(config, key)
    t = MonitorHostThread( monitorConfig, th.OperationMode.NORMAL)   
    t.start()
    
    input("Press a key to finish")
    t.stopRun()
    
    #wait thread end
    t.join()
    
    print("loopCount="+str(t.loopCount)+",loopCount="+str(t.recordsProcessed),",bytesProcessed="+str(t.bytesProcessed))
    
    print("End module execution")