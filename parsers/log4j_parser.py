# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 07:36:48 2017

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************

import re
from enum import Enum

from logmapperagent.parser.log_event import LogEvent
from logmapperagent.parser.log_event import ComponentState
from logmapperagent.parser.logmapper_parser import LogMapperParser
from logmappercommon.definitions.event_categories import LogEventCategories

#%%

LOG_REGEX=r'''
(
    (\d{4}[/.-]\d{2}[/.-]\d{2}[\s]\d{2}[:]\d{2}[:]\d{2}[.]\d+)  #Date & Time: 2017-05-13 07:57:26.013
    \s+                                                         #Space
    (\S+)                                                       #String: Thread
    \s+
    (TRACE|DEBUG|INFO|WARN|ERROR|FATAL)                         #String: Category: Solo acepta los codigos
    \s+
    (\S+)                                                       #String: Class
    \s+-                                                        #Caracter '-'. 
    \s+
    (.+[:?])?                                                   #texto que termina en : (opcional) texto principal del log
    (.+)                                                        #Texto restante          
)
'''


REMOTECALL_REGEX=r'''
^.*?\bapiTraceId=([a-f0-9-]+)
'''


USERKEY_REGEX=r'''
^.*?\buserId=([0-9]+)
'''

TENANTKEY_REGEX=r'''
^.*?\btenantId=([a-z0-9_]+)
'''



class Log4jParser(LogMapperParser):
    """
    ***************************************************************************
    
    ***************************************************************************
    """
    
    def __init__(self, host, component):
        """
        ***********************************************************************
        
        ***********************************************************************
        """              
        self.logRegexCompiled = re.compile(LOG_REGEX, re.VERBOSE)
        self.remoteCallRegexCompiled = re.compile(REMOTECALL_REGEX, re.VERBOSE)
        self.userKeyRegexCompiled = re.compile(USERKEY_REGEX, re.VERBOSE)
        self.tenantKeyRegexCompiled = re.compile(TENANTKEY_REGEX, re.VERBOSE) 
        
        self.host = host
        self.component = component
        
        self.componentState = ComponentState.NONE

#%%    
    def parse(self, text):
        """
        ***********************************************************************
        
        ***********************************************************************
        """       
        r=self.logRegexCompiled.findall(text)
        
        if not r:       
            return None
        
        timestamp = str(r[0][1])
        threadKey=str(r[0][2])
        logLevel=str(r[0][3])
        className=str(r[0][4])
#        method=None
#        lineNumber=None
        
        if not r[0][5]:
            title=str(r[0][6])          
        else:
            title=str(r[0][5])    
        
        logEvent=LogEvent(timestamp, text)
        
        logEvent.host = self.host
        logEvent.component= self.component
        
        #Fix exception when character : is 
        if ':' in title:
            title = title[0:title.find(':')]
            
        #most of time number change. Then, for logClass drop digit characters
        title = ''.join([c for c in title if not c.isdigit()])
            
        logEvent.text = title
        logEvent.className = className
        logEvent.logLevel = logLevel
        logEvent.threadKey = threadKey
        
        logEvent.key=self._getKey(logEvent)   
        logEvent.remoteCallKey=self._parseRemoteCallKey(logEvent.raw)
        logEvent.userKey=self._parseUserKey(logEvent.raw)
        logEvent.tenantKey=self._parseTenantKey(logEvent.raw)
        logEvent.eventCategory = self._getEventCategory(logEvent)

         
        return logEvent           
        
#%%
        
    def _getKey(self, data):
        """
        ***********************************************************************
        Retorna un logEvent
        ***********************************************************************
        """         
        className=data.className.replace("com.ospinternational.", "")
        logLevel=data.logLevel
        text=data.text
        code=text+"-"+logLevel+"-"+className
        return code   
   

#%%
        
    def _parseRemoteCallKey(self, data):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        if "apiTraceId" in data:
            r2=self.remoteCallRegexCompiled.findall(data)
            if r2:
                return r2[0]
            else:
                return None
            
            
            
    def _parseUserKey(self, data):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        if "userId" in data:
            r2=self.userKeyRegexCompiled.findall(data)
            if r2:
                return r2[0]
            else:
                return None
            
    def _parseTenantKey(self, data):
        """
        ***********************************************************************
        
        ***********************************************************************
        """         
        if "tenantId" in data:
            r2=self.tenantKeyRegexCompiled.findall(data)
            if r2:
                return r2[0]
            else:
                return None  
            
    def _getEventCategory(self, data):
        """
        ***********************************************************************
        
        ***********************************************************************
        """         
        if "The following profiles are active" in data.raw:
            self.componentState = ComponentState.BOOTING
            
        if self.componentState == ComponentState.BOOTING:
            
            if "CoreMain" in data.raw and "STARTED!!!" in data.raw:
                self.componentState = ComponentState.NONE
                
            if "ERROR" in data.logLevel:
                return LogEventCategories.EVENT_BOOT
            elif "WARNING" in data.logLevel:
                return LogEventCategories.EVENT_BOOT
            elif "CRITICAL" in data.logLevel:
                return LogEventCategories.CRITICAL               
            else:
                return LogEventCategories.TRACE_BOOT
        
         
        
        if "ERROR" in data.logLevel:
            if "hibernate" in data.raw:
                return LogEventCategories.DB_ERROR 
            return LogEventCategories.ERROR 
        if "WARNING" in data.logLevel:
            return LogEventCategories.WARNING  
        if "CRITICAL" in data.logLevel:
            if "hibernate" in data.raw:
                return LogEventCategories.DB_ERROR             
            return LogEventCategories.CRITICAL            
        
        #Event category not knowed
        return LogEventCategories.NONE
    

   
    
#%%
"""
*******************************************************************************

*******************************************************************************
"""

if __name__ == '__main__':

    print('Start module execution:')
    parser = Log4jParser('localhost', 'component', 'instance')
    
    logLines="""
2017-08-31 05:36:50,558 - logmapper_config.parser - DEBUG - 2017-06-26 09:57:53.978 [SimpleAsyncTaskExecutor-102] DEBUG com.ospinternational.sm.api.client.impl.concurrent.ConcurrentClientImplCommon - Response:ConcurrentStateResponse [data=QUEUEDSmBaseResponse [response=OK, errorCode=null, errorDescription=null, apiTraceId=e38b4efb-aece-4e30-987c-ffe4b9b83265]]
2017-06-26 09:13:04.352 [main] INFO  com.ospinternational.sm.service.bean.impl.transaction.TransactionServiceImpl - saveEvaluationCode:EvaluationCode [id=null, code=WARNING, name=WARNING]
2017-06-26 09:13:04.352 [main] DEBUG com.ospinternational.sm.service.bean.impl.transaction.TransactionServiceImpl - validateEvaluationCode:EvaluationCode [id=null, code=WARNING, name=WARNING]
2017-06-26 10:01:48.959 [SimpleAsyncTaskExecutor-342] DEBUG com.ospinternational.sm.appcode.core.business.impl.DeviceTypeTokCoreBusinessImpl - Termina perform
2017-11-09 03:31:28.576 [https-jsse-nio-4007-exec-2] DEBUG com.ospinternational.sm.core.business.impl.common.SmCoreSecurityBussinesNoneImpl - checkSecurity: SECURITY-CORE:getByParentStringOrderByOrder>SmSecurityParameter [code=MENU_HEADERSmBaseParameter [header=ApiHeader [userId=2, source=APPCODE-TRX-WEB-1, externalUser=null, apiTraceId=e21f0342-e7cc-4baf-907e-190df4c7f5d9]]]
2017-11-09 03:07:24.988 [main] INFO  com.ospinternational.sm.SecurityCoreMain - The following profiles are active: local,ssl
2017-11-09 03:07:39.309 [main] INFO  com.ospinternational.sm.SecurityCoreMain - ********** SECURITY-CORE-(4.7.433) STARTED!!! **********
2017-11-09 03:07:39.309 [main] WARN  com.ospinternational.sm.SecurityCoreMain - No se obtuvo parametro ENABLED de microservicio de parametros:SmApiException:  code: SM_API_CORE_UNAVAILABLE type: FAIL category: EXT message: Micro-Servicio No disponible detail: Service PARAMETER-CORE Not available
2018-01-08 13:52:00.060 [SimpleAsyncTaskExecutor-22899] INFO  com.ospinternational.sm.api.client.impl.manager.ManagerClientImpl - processTask:StringParameter [data=null]SmBaseParameter [header=ApiHeader [userId=1, source=NOTIFICATION-CORE, tenantId=smscada_vjurado_ospinternational_com, apiTraceId=3e5ed0d0-855d-4dc2-8a4f-a121303e2565]]
2018-02-26 06:02:18.032 [SimpleAsyncTaskExecutor-9975] INFO  com.ospinternational.sm.service.bean.impl.transaction.TransactionServiceImpl - finishTransaction: 11934, finishType: OK
"""
       
    for line in logLines.split("\n"):
        print('\n==================================================')
        print('\nParse line:\n'+line)
        parsed=parser.parse(line)
        print('\nParsed='+str(parsed))
        if parsed:
            print('\nText='+str(parsed.text))
       
        
    print("End module execution")