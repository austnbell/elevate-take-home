# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 15:56:58 2022

@author: Austin Bell
"""

from app.IncidentsPipeline import IncidentsPipeline
import schedule
import time

pipe = IncidentsPipeline()
schedule.every(15).minutes.do(pipe.pipeline)

while 1:
    schedule.run_pending()
    time.sleep(1)
    
    
