# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:41:32 2017

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

import logmapperagent.control.cli as cli


logger = logging.getLogger(__name__)

class QuitCommand(cli.LogMapperCommandDefinition):

    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        pass
    
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    commandDefinition = QuitCommand("quit", "q", "Help")
    commandDefinition.parseArgs("quit") 
    response = commandDefinition.execute()
    print(str(response))
    
    print("End module execution")