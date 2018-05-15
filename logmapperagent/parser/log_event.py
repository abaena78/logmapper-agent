# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 17:25:52 2017

@author: abaena
"""

from enum import Enum

class LogEvent:
    
    def __init__(self, timestamp, raw):
        
        #Raw data of the line parsed
        self.raw=raw          
                
        #Timestamp when the node happen
        self.timeexec=timestamp
        
        #Host name identifier
        self.host=None        
        
        #Name of executable component 
        self.component=None

        #Name of Class        
        self.className=None
        
        #Name of Method, Function or Routine
        self.method=None
        
        #Source code Number of line
        self.lineNumber=None
        
        #Log Level: DEBUG, INFO, ERROR
        self.logLevel=None 
        
        #Main text of the log
        self.text=None   
        
        # Key or Unique code that identify the node
        self.key = None        
        
        #Log item category: trace, event, error, etc.
        self.eventCategory = None
        
        #Thread Code Identifier
        self.threadKey=None        
        
        #Inter process Call Identifier
        self.remoteCallKey=None
        
        #User Name
        self.userKey=None        
        
        #Tenant key for multitenant Systems
        self.tenantKey=None   
        
   
        
        
    def __str__(self):
        return ("LogEvent:["  
                           "  key="+str(self.key) +
                           ", timeexec="+str(self.timeexec) +
                           ", threadKey="+str(self.threadKey)+
                           ", eventCategory="+str(self.eventCategory)+
                           ", remoteCallKey="+str(self.remoteCallKey) +
                           ", userKey="+str(self.userKey) +
                           ", tenantKey="+str(self.tenantKey) +
                           "]"
        )
        
        
class ComponentState(Enum):
    NONE = 0
    BOOTING = 1
    FAIL = 2
        
