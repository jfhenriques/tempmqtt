

def calculate_res_mean(val1, val2, res = 2):
   if res < 2:
      res = 2
   return ((val1 * (res-1)) / res) + (val2 / res)
   
class Reading:
   def __init__(self, temp = None, hum = None, press = None):
      self.temp = temp
      self.hum = hum
      self.press = press

   
class TempSensor:
   def __init__(self):
      pass
      
   def readData(self):
      pass
      
   def parseData(self):
      pass