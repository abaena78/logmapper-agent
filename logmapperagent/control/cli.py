# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 13:32:38 2017

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
import enum


#from lmpa_commands import *

#%%
"""
Global Initialization. Constants definitions.
"""


MSG_PROMPT="Type Command>>>"
END_LINE = '\r\n' 
MSG_PROCESSING = "Processing..."   

class LogMapperCliErrors(enum.Enum):
    OK = 0
    INVALID_COMMAND = 1
    INVALID_PARAMETER = 2
    TIMEOUT = 3
    EXCEPTION = 4

#%%

logger = logging.getLogger(__name__)

class LogMapperCommandDefinition:
    
    def __init__(self, command, shortCommand, shortDescription, closeSession=False, putInQueue=True, waitQueueTx=True):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        self.command = command
        self.shortCommand = shortCommand
        self.shortDescription = shortDescription
        
        #Close session after execute command
        self.closeSession=closeSession
        
        #Put Command in Queue
        self.putInQueue=putInQueue
        
        #Response must be sent for another process. Wait Queue Response
        self.waitQueueTx=waitQueueTx 
        
        self.inputData=None
        self.arg1=None        

    def __str__(self):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        formatstr = "{:<15} [ {:<5}] : {}"
        return formatstr.format( self.command, 
                                self.shortCommand, 
                                self.shortDescription)
        pass
    
    def parseArgs(self, inputData):
        """
        ***********************************************************************
        
        ***********************************************************************
        """
        #Initial Command Line Request
        self.inputData=inputData.strip().lower()
        self.arg1=None
        self.args=None
        
        inputDataArray = inputData.split()
        
        if len(inputDataArray) > 1:
            self.arg1=inputDataArray[1]
            self.args=inputDataArray[1:]
        
        
    
    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        pass   


class LogMapperCommandResponse:
    
    def __init__(self, succes, response=None):
        
        #LogMapperCommandDefinition object
        self.command=None
        
        #Succes or fail executing command
        self.success=None
        
        #Error Detail String
        self.errorDetail=None
        
        #Response String
        if succes:
            self.response=response
        else:
            self.response="ERROR: "+response
        
    def __str__(self):
        string = 'SUCCESS: ' + str(self.success)
        if self.errorDetail:
            string += '\nERROR:'+str(self.errorDetail)        
        if self.response:
            string += '\n'+str(self.response)
        return string
        



def getCommandDefinition(inputData, commandList):
    """
    Syntax Validation of the command
    Return True is command is valid. Otherwise False.
    """ 
    inputData=inputData.strip().lower()
    
    inputDataArray = inputData.split()
    
    if len(inputDataArray) == 0:
        return None
    
    for item in commandList:
        if inputDataArray[0] == item.command or inputDataArray[0] == item.shortCommand:
            return item
    
    return None  


def getWelcome():
    """
    print LogMapper Agent Menu 
    """    
    return "\r\n### LogMapper AGENT Command Line Interface ### (? : Help)\r\n"   


def getPrompt():
    """
    print LogMapper Agent Menu 
    """    
    return "\r\n>>"  

def getErrorMsg(error=None, detail=None):
    """
    print LogMapper Agent Menu 
    """    
    msg = "ERROR"
    if error:
        msg = msg + ": " + str(error)
    if detail:
        msg = msg + " Detail: " + str(detail)        
    return msg 
          
          
#%%
if __name__ == '__main__':  
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    import logmapperagent.commands.commands_index as cmd
    
    print(getWelcome())
    inputData = input(getPrompt())
    commandDefinition = getCommandDefinition(inputData, cmd.COMMAND_LIST)
    print("getCommandDefinition:"+str(commandDefinition))

    if commandDefinition:
        commandDefinition.parseArgs(inputData)
        print("arg1="+str(commandDefinition.arg1))        
        commandDefinition.execute(None)
    else:
        print(getErrorMsg(LogMapperCliErrors.INVALID_COMMAND, inputData))
        
    print("End module execution")
    