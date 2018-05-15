#!/usr/bin/python3
# -*- coding: utf-8 -*-

#LogMapper
#
#MIT License
#
#Copyright (c) 2018 Jorge A. Baena - abaena78@gmail.com
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""
===============================================================================
Main Control Loop for LogMapper Agent

@author: Jorge Andres Baena
@contact	: www.logmapper.org
@copyright: "Copyright 2018, The LogMapper Project"
@license: "GPL"
@date:	7/04/2018
===============================================================================
"""

import os
import logging
import argparse

import config.config as cfg
import logmappercommon.utils.logging_util as logging_util
import logmapperagent.control.main_control as control

#%%
#==============================================================================
# Global Initialization.
#==============================================================================

logger = logging.getLogger(__name__)


#%%
#==============================================================================
# Functions.
#==============================================================================

def processArguments():
    """ 
    ===========================================================================
    Parse command Line arguments 
    =========================================================================== 
    If args are invalid return false, and program must exit    
    
    **Args**:
        None
    **Returns**:
        True if args are valid. Otherwise False -- (boolean)
    """             

    parser = argparse.ArgumentParser(prog="LogMapper Agent")   
    parser.add_argument("-rc", "--reset-config", dest="resetconfig",
                        help="Reset configuration settings", action="store_true")
    parser.add_argument("-c", "--config", dest="configfilename", required=False,
                    help="specific config file")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+cfg.__version__)
  
    args = parser.parse_args()
    
        
    if args.configfilename:
        if not os.path.exists(args.configfilename):
            parser.error("The file %s does not exist!" % args.configfilename)        
            
    return args


#%%
def main(): 
    """ 
    ===========================================================================
    logmappper-agent **Main** function 
    ===========================================================================   
    Aqui un ejemplo de documentacion
    Formatos: *cursiva* 
    ``code = True``
    
    **Args**:
        * config: configuration object        
    **Returns**:
        None   
    """
    
    args = processArguments()  

    config=cfg.loadConfig(args.configfilename, args.resetconfig)  
    logMapperAgentConfig = cfg.loadLogMapperAgentConfig(config)
        
    logging_util.configureLogger(logMapperAgentConfig.logFilePath) 
      
    logger.info("Start LogMapper Agent")
    
    cfg.printConfig(config)
    
    control.initApplication(config)
    
    control.startApplicationTask(config)
      
    control.mainLoop(config)
    
    control.stopApplicationTask(config)      
      
    logger.info("Finish LogMapper Agent")

#%%
#==============================================================================
# main
#==============================================================================
    
if __name__ == '__main__':
    main()