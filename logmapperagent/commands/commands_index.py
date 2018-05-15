# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 05:12:06 2017

@author: abaena
"""

#******************************************************************************
#Add logmapper-agent directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..'))) 
#******************************************************************************


from logmapperagent.commands.quit import QuitCommand
from logmapperagent.commands.help import HelpCommand
from logmapperagent.commands.stop import StopCommand
from logmapperagent.commands.start import StartCommand
from logmapperagent.commands.show import ShowCommand
from logmapperagent.commands.get import GetCommand
from logmapperagent.commands.set import SetCommand




COMMAND_LIST = [ 
        QuitCommand("quit", "q", "Quit terminal. LogMapper still running", True),
        HelpCommand("help", "?", "Help"),
        StopCommand("stop", "sto", "Stop services. Options: readers, monitors, reader <key>, threads, logmapper"),
        StartCommand("start", "sta", "Start services. Options: map <key>, readers, mappers, monitors, register"),
        ShowCommand("show", "sh", "Show Info. Options: status, readers, host, cfg"),
        GetCommand("get", "g", "Get Data. Options: agent, readers, monitors, logkeys, paths, pathMeasures, logEventsCount, logMetrics, monMeasures, logRecords"),
        SetCommand("set", "s", "Set Data. Options: ds, se. Values: <0|1>")
        ]

#%%
if __name__ == '__main__':
    for cmd in COMMAND_LIST:
        print(str(cmd))
