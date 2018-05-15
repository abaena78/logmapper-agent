# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:40:59 2017

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


class HelpCommand(cli.LogMapperCommandDefinition):

    def execute(self, config=None):
        """
        ***********************************************************************
        
        ***********************************************************************
        """ 
        from logmapperagent.commands.commands_index import COMMAND_LIST
        response = ''
        for item in COMMAND_LIST:
            response += str(item)+"\r\n"            
        return cli.LogMapperCommandResponse(True, response)
    
#%%
if __name__ == '__main__':
    print('Start module execution:')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    commandDefinition = HelpCommand("help", "?", "Help")
    commandDefinition.parseArgs("help")            
    response = commandDefinition.execute()
    print(str(response))
    
    print("End module execution")