
from Reading import Reading

def calculate_res_mean(val1, val2, res = 2):

   if val1 is None and val2 is None:
      return None
   elif val1 is None:
      return val2
   elif val2 is None:
      return val1
      
   if res < 2:
      res = 2

   return ((val1 * (res-1)) / res) + (val2 / res)   

class TempReading(Reading):
   def __init__(self, humidity = None, temperature = None, pressure = None, timestamp = None):
      self.temperature = temperature
      self.humidity = humidity
      self.pressure = pressure

   def getReadingName(self):
      return 'temperature'

   def getDict(self):
      return self.__dict__

   def getAltitude(self, seaLevelpressure):
      if self.pressure is None or seaLevelpressure is None:
         return None
      return 44330 * (1.0 - math.pow(self.pressure / seaLevelpressure, 0.1903))

      
   
class TempSensor():
   def __init__(self):
      pass
      
   def readData(self):
      pass
      
   def parseData(self, reading):
      pass
