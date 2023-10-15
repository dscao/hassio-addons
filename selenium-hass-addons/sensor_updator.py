import requests
from const import *
import logging
import os


class SensorUpdator:

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.token = token
    
    def update(self, sensorName: str, sensorState:float, sensorattributes: str):
        token = os.getenv("SUPERVISOR_TOKEN") if self.base_url == SUPERVISOR_URL else self.token
        headers = {
        "Content-Type": "application-json",
        "Authorization": "Bearer " + token 

        }
        request_body = {
            "state":sensorState,
            "attributes": sensorattributes
        }
        url = self.base_url + API_PATH + sensorName

        try:        
            response = requests.post(url, json = request_body, headers = headers)
            logging.info(f"Homeassistant REST API invoke, POST on {url}. response[{response.status_code}]: {response.content}")
        except:
            raise Exception("Sensor update failed, please check the network")
            
class SensorentityUpdator:

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.token = token
    
    def update(self, sensorName: str, sensorState:float, sensorattributes: str):
        token = os.getenv("SUPERVISOR_TOKEN") if self.base_url == SUPERVISOR_URL else self.token
        headers = {
        "Content-Type": "application-json",
        "Authorization": "Bearer " + token 

        }
        request_body = {
            "state":sensorState,
            "attributes": sensorattributes
        }
        url = self.base_url + API_PATH + sensorName

        try:        
            response = requests.post(url, json = request_body, headers = headers)
            logging.info(f"Homeassistant REST API invoke, POST on {url}. response[{response.status_code}]: {response.content}")
        except:
            raise Exception("Sensor update failed, please check the network")
