
import os
import psutil
from datetime import datetime, timezone
import tzlocal
from Reading import Reading
import json


RPI_TEMP_FILE = '/sys/class/thermal/thermal_zone0/temp'
RPI_THRO_FILE = '/sys/devices/platform/soc/soc:firmware/get_throttled'



def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def get_cpu_temp():
    with open(RPI_TEMP_FILE, "r") as f:
        return round(int(f.readline()) / 1000, 1)

def get_throttled():
    _throttled = open(RPI_THRO_FILE, 'r').read()[:-1]
    return _throttled[:4]


class SystemReading(Reading):

   def getReadingName(self):
      return 'system'

   def getDict(self):
      return self.__dict__
   

class SystemSensor():

   def readData(self, isRPI = True, reading = SystemReading()):

      reading.load_15 = round(os.getloadavg()[2], 2)

      if isRPI:
         reading.throttled = get_throttled()

         reading.cpu_temperature = get_cpu_temp()

      reading.memory_use_percent = psutil.virtual_memory().percent

      reading.swap_use_percent = psutil.swap_memory().percent

      reading.disk_user_percent = psutil.disk_usage('/').percent

      reading.last_boot = utc_to_local(datetime.utcfromtimestamp(psutil.boot_time())).isoformat()

      return reading 

