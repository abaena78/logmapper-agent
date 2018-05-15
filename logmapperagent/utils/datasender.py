# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 21:17:19 2018

@author: abaena
"""

import logging
import requests
import threading

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()
headers = {'Content-type': 'application/json;charset=utf-8', 'Accept-Encoding': 'gzip,deflate'} # 'Accept': 'text/plain' charset=utf-8


def saveData(host, port, dataType, json):
    url = "http://"+host+":"+str(port)+"/save/"+dataType
    response = requests.post(url, headers=headers, json=json, verify=False)
    if response.status_code != 200:
        return("Error: {}".format(response.status_code))
    else:
        return response.json() 
    
class DataSenderThread(threading.Thread):
    
    def __init__(self, name, host, port, dataType, data):
        threading.Thread.__init__(self)
        self.setName("TX_"+name)
        self.host = host
        self.port = port
        self.dataType = dataType
        self.data = data
        
    def run(self):
        logger.debug ("Start Thread:" + self.name)  
        try:
            r = saveData(self.host, self.port, self.dataType, self.data)
            logger.debug(str(r))
        except Exception as exc:
            logger.error("Exception in "+self.name+":"+str(exc))     
            
        logger.debug ("End Thread:" + self.name)          
    
  
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
    
    d={"a": "b"}
    
    #r = sendData("localhost", 5005, d)
    #print(r)    
    
    sender = DataSenderThread("test", "localhost", 5005, "hostmet", d)
    sender.start()
    logger.debug("test")


