# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 13:36:55 2017

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************

import sys
import logging
import threading
import socket
import queue
import time

#import lmpa_control.command_handler as cmd

import logmapperagent.control.cli as cli
import logmapperagent.commands.commands_index as cmd





#%%
"""
Global Initialization. Constants definitions.
"""

#MSG_WELCOME='\n\rWelcome to logmapper-agent'
#MSG_PROMPT="\n\rType Command>>>"
ENCODING='utf-8'
NEWLINE='\r\n'

TIMEOUT_SECONDS=60

logger = logging.getLogger(__name__)

queueRxSocketServer = queue.Queue()
queueTxSocketServer = queue.Queue()


#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    printMessage(conn, cli.getWelcome())
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:        
        printMessage(conn, cli.getPrompt()) #send only takes string
        endLine=False
        inputData=''
        while not endLine:            
            #Receiving from client
            inputData += conn.recv(1024).decode(ENCODING)
            if '\n' in inputData:
                break
            
        inputData = inputData.strip()
        if not inputData:
            continue  
        
        while not queueTxSocketServer.empty():
            logger.warning("data tx lost:" + str(queueTxSocketServer.get()))        
        
        commandDefinition = cli.getCommandDefinition(inputData, cmd.COMMAND_LIST)
        
        if not commandDefinition:
            printMessage(conn, NEWLINE+cli.getErrorMsg(cli.LogMapperCliErrors.INVALID_COMMAND, inputData))
            continue
        
        logger.info("getCommandDefinition:"+str(commandDefinition))
         
        printMessage(conn, NEWLINE+"Start Command Execution: "+commandDefinition.command)
        
#        conn.sendall(bytes("\n\rSuccess: "+str(processCommandResponse.success), ENCODING))
#        if processCommandResponse.response:
#            conn.sendall(bytes("\n\rResponse:" + processCommandResponse.response, ENCODING))     
        
        if commandDefinition.closeSession:
            break
        
        #put command in Queue and close connection
#        if processCommandResponse.commandRequestCode == cmd.CMD_KILL['cmd']:
#            queueRxSocketServer.put(processCommandResponse.commandRequestCode)
#            break      

        if commandDefinition.putInQueue:
            queueRxSocketServer.put(inputData)  
        
        if commandDefinition.waitQueueTx:
            timeout=False
            counter = 0
            while queueTxSocketServer.empty():
                time.sleep(1)
                counter += 1
                if counter > TIMEOUT_SECONDS:
                    timeout=True
                    break
                
            if timeout:
                printMessage(conn, NEWLINE+cli.getErrorMsg(cli.LogMapperCliErrors.TIMEOUT))
            else:
                logMapperCommandResponse = queueTxSocketServer.get()
                printMessage(conn, NEWLINE+"LMData:"+NEWLINE+logMapperCommandResponse.response+NEWLINE+"LMEndData")            
     
    #came out of loop
    printMessage(conn, NEWLINE+"Bye") 
    conn.close()
    
def printMessage(conn, message):
   """
   print LogMapper Agent Menu 
   """    
   conn.send(bytes(message, ENCODING)) #send only takes string
    
class SocketServerSessionThread (threading.Thread):
    """
    Thread for Command Line Interface (CLI)
    """
    def __init__(self, name, conn):
        threading.Thread.__init__(self)
        self.setName(name)
        self.conn=conn
    def run(self):
        logger.debug ("Start SocketServerSessionThread:" + self.name)
        try:
            clientthread(self.conn)
        except:
            logger.exception("Server thread exception" + str(sys.exc_info()))
            printMessage(self.conn, NEWLINE+cli.getErrorMsg(cli.LogMapperCliErrors.EXCEPTION))
            self.conn.close()
    

class SocketServerThread (threading.Thread):
    """
    Thread for Command Line Interface (CLI)
    """
    def __init__(self, name, port):
        threading.Thread.__init__(self)
        self.setName(name)
        self._stopRun = False
        self.port = port
        
    def stopRun(self):
        """
        Ask thread end safely
        """
        logger.debug("stopRun:")
        self._stopRun = True        
        
    def run(self):
        logger.debug ("Start Thread:" + self.name)
        HOST = ''   # Symbolic name meaning all available interfaces
         
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.debug('Socket created')
         
        #Bind socket to local host and port
        try:
            server.bind((HOST, self.port))
        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
             
        logger.debug('Socket bind complete')
         
        #Start listening on socket
        server.listen(1)
        logger.debug('Socket now listening')
        
         
        #now keep talking with the client
        while not self._stopRun:
            #wait to accept a connection - blocking call
            conn, addr = server.accept()
            
            if self._stopRun:
                conn.close()
                break
            
            logger.debug ('Connected with ' + addr[0] + ':' + str(addr[1]))
             
            #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
            thread=SocketServerSessionThread("SOCKET_SESSION", conn)
            thread.start()
         
        #TODO Cerrar todos los hilos abiertos
        server.close() 
        logger.debug('Server closed')



def checkServerClosed():
    logger.debug('checkServerClosed')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 5001))
        sent = sock.send(bytes("\r\n", ENCODING))
        sock.close()
    except Exception as e:
        logger.warn("Error:"+str(type(e)) + ":"+str(e))
    
"""
*******************************************************************************

*******************************************************************************
"""

if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

    serverPort = 5001    
    socketServerThread = SocketServerThread("SERVER", serverPort)
    socketServerThread.start()  
    
    print("Server running on port "+str(serverPort))
    input("Press key to finish")
    
    socketServerThread.stopRun()
    checkServerClosed()   
    
    print("End module execution")
      
       