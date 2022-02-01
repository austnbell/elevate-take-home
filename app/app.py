# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 14:33:00 2022

@author: Austin Bell
"""


from fastapi import FastAPI
import json
import uvicorn

incidents = FastAPI(title="incidents")


@incidents.get("/incidents")
def get_incidents():
    with open("./data/incidents.json", "r") as f:
        historical_incidents = json.load(f)
        
    return historical_incidents

if __name__ == "__main__":
    uvicorn.run(incidents, host="0.0.0.0", port=9000)