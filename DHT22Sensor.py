
from TempSensorReading import *
from time import sleep
import Adafruit_DHT
from datetime import datetime


class DHT22Sensor(TempSensor):
   
   def __init__(self, GPIO, sensor_sleep_secs = 2.0):
      self.temp_hist = {"val": None, "in_mean": None}
      self.hum_hist  = {"val": None, "in_mean": None}
      self.last_sensor_read = None
      self.sensor_sleep_secs = sensor_sleep_secs
      self.GPIO = GPIO
      self.good_tries = 15
      self.total_tries = 1
      self.lastReading = None
      self.temp_threshold = 1.0
      self.hum_threshold = 5.0
      self.history_size = 3
      self.roundDigits = 1
      self.smoothData = True
      
   def readData(self):
      t = 0.0
      tt = 0
      h = 0.0
      ht = 0
      
      if self.lastReading is None:
         self.lastReading = TempReading()

      for i in range(self.total_tries):
         if self.last_sensor_read is not None:
            secs_passed = float((datetime.now() - self.last_sensor_read).total_seconds())
            if secs_passed < self.sensor_sleep_secs:
               sleep(self.sensor_sleep_secs - secs_passed)
      
         humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22, self.GPIO)
         self.last_sensor_read = datetime.now()
         if humidity is not None and humidity <= 105.0 and humidity >= -5.0:
            h += humidity
            ht += 1

         if temperature is not None and temperature <= 95.0 and temperature >= -20.0:
            t += temperature
            tt += 1

         if ht >= self.good_tries and tt >= self.good_tries:
            break

      if tt > 0 and ht > 0:
        self.lastReading.temperature = float(t/tt)
        self.lastReading.humidity = float(h/ht)
        return True
      
      return False
      
   def parse_value(self, val, hist, threshold):
      if val is None:
         return None

      if hist['val'] is None:
         hist["val"] = val
         hist["in_mean"] = val
         return round(val, self.roundDigits)
      
      if val >= (hist["in_mean"] - threshold) and val <= (hist["in_mean"] + threshold):
         hist["val"] = TempSensor.calculate_res_mean(val, hist["val"], self.history_size)
         hist["in_mean"] = hist["val"]
        
         return round(hist["val"], self.roundDigits)
        
      else:
         l_thr = hist["val"] - threshold
         u_thr = hist["val"] + threshold

         if val < l_thr:
            val = l_thr
         elif val > u_thr:
           val = u_thr

         hist["in_mean"] = TempSensor.calculate_res_mean(val, hist["in_mean"], self.history_size)
      return None
   
   def parseData(self, reading = TempReading()):
      if self.lastReading is not None and self.lastReading.temperature is not None and self.lastReading.humidity is not None:
      
         if self.smoothData:
            temp = self.parse_value(self.lastReading.temperature, self.temp_hist, self.temp_threshold)
            hum = self.parse_value(self.lastReading.humidity, self.hum_hist, self.hum_threshold)
            if temp is not None and hum is not None:
               reading.humidity = hum
               reading.temperature = temp
               return reading
         else:
            reading.humidity = round(self.lastReading.temperature, self.roundDigits)
            reading.temperature = round(self.lastReading.humidity, self.roundDigits)
            return reading
      
      return None
      
