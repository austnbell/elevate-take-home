# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 12:39:32 2022

@author: Austin Bell
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

class IncidentsPipeline():
    
    base_url = "https://incident-api.use1stag.elevatesecurity.io/"
    incident_endpoint = base_url + "incidents/"
    incident_types = ['denial', 'intrusion', 'executable', 'misuse', 'unauthorized',
                      'probing', 'other']
    
    identities_url = base_url + "identities/"
    
    data = "incidents.json"
    
    def authorize(self):
        self.username = "PLACEHOLDER"
        self.password = "PLACEHOLDER"
        
    def get_identities(self):
        r = requests.get(self.identities_url, auth=HTTPBasicAuth(self.username, self.password))
        identities_dict = json.loads(r.text)
        
        return identities_dict
    
    def load_historical_incidents(self):
        with open("./data/incidents.json", "r") as f:
            historical_incidents = json.load(f)
            
        return historical_incidents 
    
    def extract_raw_incident(self, incident_type):
        url = self.incident_endpoint +  incident_type
        r = requests.get(url, auth=HTTPBasicAuth(self.username, self.password))
        raw_incident = json.loads(r.text)['results']
        
        return raw_incident
    
    def get_employee_id(self, identities, incident):
        # check if ip address 
    
        if 'reported_by' in incident.keys():
            employee_id = incident['reported_by']
        
        elif 'employee_id' in incident.keys():
            employee_id = incident['employee_id']
            
        elif 'identifier' in incident.keys():
            employee_id = incident['identifier']
            try: 
                employee_id = identities[employee_id]
            except KeyError:
                pass
        
        else:
            ip = self.get_ip(incident)
            try: 
                employee_id = identities[ip]
            except KeyError:
                print("IP Address does not exist in identities: " + str(ip))

        return employee_id
    
    def get_ip(self, incident):
        if 'internal_ip' in incident.keys():
            return incident['internal_ip']
        
        elif 'source_ip' in incident.keys():
            return incident['source_ip']  
        
        elif 'machine_ip' in incident.keys():
            return incident['machine_ip']
        
        elif 'ip' in incident.keys():
            return incident['ip']
        
    
    def add_new_incident(self, historical_incidents, employee_id, incident, incident_type):
        # pull historical value
        try:
            employee_incidents = historical_incidents[employee_id]
            
        # or create new entry
        except KeyError:
            employee_incidents =  {
                            "low": {
                                    "count": 0,
                                    "incidents": []
                                    },
                            "medium": {
                                    "count": 0,
                                    "incidents": []
                                    },
                            "high": {
                                    "count": 0,
                                    "incidents": []
                                    },
                            "critical": {
                                    "count": 0,
                                    "incidents": []
                                    }
                            }
        
        
        incident_report = {
                "type": incident_type,
                "priority": incident['priority'],
                "machine_ip": self.get_ip(incident),
                "timestamp": incident['timestamp']
                }
        
        priority = incident['priority']
        employee_incidents[priority]['count'] += 1
        employee_incidents[priority]['incidents'].append(incident_report)
        sorted(employee_incidents[priority]['incidents'], key=lambda d: d['timestamp']) # poor approach to sorting
        
        # update historical incidents
        historical_incidents[employee_id] = employee_incidents
        
        return historical_incidents                   
        
                
    
    def process_incidents(self, historical_incidents, raw_incident, identities, incident_type):
        for incident in raw_incident:
            
            #print(incident)
            employee_id = self.get_employee_id(identities, incident)
            
            # pull out and add new incident
            historical_incidents = self.add_new_incident(historical_incidents, employee_id, incident, incident_type)
            
            
        return historical_incidents
        
    
    def save_incidents(self, historical_incidents):
        with open("./data/incidents.json", "w") as f:
            json.dump(historical_incidents, f)
            #f.write(str(historical_incidents))
        
    
    def pipeline(self):
        print("processing")
        self.authorize()
        
        identities = self.get_identities()
        historical_incidents = {}
        #historical_incidents = self.load_historical_incidents()
        
        for incident_type in self.incident_types:
            raw_incident = self.extract_raw_incident(incident_type)
            historical_incidents = self.process_incidents(historical_incidents, raw_incident, identities, incident_type)
            
            
        self.save_incidents(historical_incidents)
        print("complete")
        

if __name__ == "__main__":
    pipe = IncidentsPipeline()
    pipe.pipeline()
    