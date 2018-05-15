# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 20:35:07 2017

@author: abaena
"""

import logging


logger = logging.getLogger(__name__)


def createTablesBase(conn):
    """
    Create tables mapper logmapper
    """    
    cursor = conn.cursor()        
      
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmp_monitor_host_dataT
        (
          id INTEGER PRIMARY KEY,
          exectime TEXT,         
          cpu REAL,
          cpu_user REAL,
          cpu_sys REAL,
          cpu_idle REAL,
          mem REAL,
          swap REAL,
          diskusage REAL,
          pids INTEGER,
          cnxs INTEGER,
          users INTEGER,
          disk_io_count_w INTEGER,
          disk_io_count_r INTEGER,
          net_io_count_s INTEGER, 
          net_io_count_r INTEGER,  
          net_err_in INTEGER,
          net_err_out INTEGER,
          net_drop_in INTEGER,
          net_drop_out INTEGER, 
          openfiles INTEGER,
          disk_io_rate_w REAL,
          disk_io_rate_r REAL,
          net_io_rate_s REAL,
          net_io_rate_r REAL,
          net_err_rate_in REAL,
          net_err_rate_out REAL,
          net_drop_rate_in REAL,
          net_drop_rate_out REAL,
          openfiles_rate REAL
        )
    ''') 
         
    conn.commit() 
    cursor.close()
    
def insertMeasure(cursor, queryData):
    cursor.execute(
    """
    INSERT INTO lmp_monitor_host_dataT(exectime, 
    cpu, cpu_user, cpu_sys, cpu_idle,
    mem, swap, diskusage, pids, cnxs, users, 
    disk_io_count_w, disk_io_count_r, net_io_count_s, net_io_count_r,
    openfiles,
    net_err_in, net_err_out, net_drop_in, net_drop_out,
    disk_io_rate_w, disk_io_rate_r, net_io_rate_s, net_io_rate_r, 
    net_err_rate_in, net_err_rate_out, net_drop_rate_in, net_drop_rate_out,
    openfiles_rate
    ) 
    VALUES (?, 
    ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, 
    ?,
    ?, ?, ?, ?, 
    ?, ?, ?, ?, 
    ?, ?, ?, ?, 
    ?, ?, ?, ?,
    ?
    );
    """
    , queryData)    