
from datetime import datetime
import tzlocal
import json

def calculate_res_mean(val1, val2, res = 2):
   if res < 2:
      res = 2
   return ((val1 * (res-1)) / res) + (val2 / res)
   
 
class Reading():
   def __init__(self, humidity = None, temperature = None, pressure = None, timestamp = None):
      self.temperature = temperature
      self.humidity = humidity
      self.pressure = pressure
      self.timestamp = timestamp

   def toJSON(self, timestamp = True):
      if timestamp:
         self.timestamp = datetime.now(tzlocal.get_localzone()).isoformat()
      return json.dumps(self.__dict__)
      
   def getAltitude(self, seaLevelpressure):
      if self.pressure is None or seaLevelpressure is None:
         return None
      return 44330 * (1.0 - math.pow(self.pressure / seaLevelpressure, 0.1903))

      
   
class TempSensor:
   def __init__(self):
      pass
      
   def readData(self):
      pass
      
   def parseData(self, reading):
      pass