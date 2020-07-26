
import os
import psutil
from datetime import datetime, timezone
import tzlocal
from Reading import Reading
import subprocess

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

def get_dir_size(path):
   try:
      return int(subprocess.check_output(['du','-sx', path]).split()[0].decode('utf-8'))
   except:
      return None

class SystemReading(Reading):

   def getReadingName(self):
      return 'system'

   def getDict(self):
      return self.__dict__
   

class SystemSensor():

   def __init__(self, isRPI = True, dirList = [], dirReadMinSeconds = 600):
      self._isRPI = isRPI
      self._dirList = dirList
     
      self._dirReadMinSeconds = dirReadMinSeconds
      self._dirLastCheckDate = None
      self._dirCacheSizes = {} 

      self._lastBoot = utc_to_local(datetime.utcfromtimestamp(psutil.boot_time())).isoformat()

   def readData(self, reading = SystemReading()):

      reading.processor_use = round(psutil.cpu_percent(interval=None))
      reading.load_5 = round(os.getloadavg()[1], 2)
      reading.load_15 = round(os.getloadavg()[2], 2)

      if self._isRPI:
         reading.throttled = get_throttled()

         reading.cpu_temperature = get_cpu_temp()

      reading.memory_use_percent = psutil.virtual_memory().percent

      reading.swap_use_percent = psutil.swap_memory().percent

      reading.disk_use_percent = psutil.disk_usage('/').percent

      reading.last_boot = self._lastBoot

      self._readDirSizes(reading)

      return reading 

   def _readDirSizes(self, reading):

      if self._dirList:

         if self._dirLastCheckDate is None or int((datetime.now() - self._dirLastCheckDate).total_seconds()) >= self._dirReadMinSeconds:
            self._dirCacheSizes = {}

            for d in self._dirList:
               self._dirCacheSizes[d] = get_dir_size(d)

            self._dirLastCheckDate = datetime.now()

         reading.dir_sizes = self._dirCacheSizes

# call main
#if __name__ == '__main__':
#   sensor = SystemSensor(True, ["/var/log"])
#   d = sensor.readData()
#   print(d.getDict()) 
