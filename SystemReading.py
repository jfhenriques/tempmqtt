
import os
import psutil
from datetime import datetime, timezone
import tzlocal
from Reading import Reading
import subprocess

RPI_TEMP_FILE = '/sys/class/thermal/thermal_zone0/temp'
RPI_THRO_FILE = '/sys/devices/platform/soc/soc:firmware/get_throttled'


# based on https://github.com/home-assistant/core/blob/dev/homeassistant/components/systemmonitor/sensor.py
IO_COUNTER = {
    "network_out": 0,
    "network_in": 1,
    "packets_out": 2,
    "packets_in": 3,
    "tp_net_out": 0,
    "tp_net_in": 1,
}


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

   def __init__(self, isRPI = True, netIfaces = [], dirList = [], dirReadMinSeconds = 600):
      self._isRPI = isRPI
      self._dirList = dirList

      self._netIfaces = netIfaces
      self._netIfacesLast = {}
      self._ifacesLastCheckDate = None

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
      self._readNetIfaces(reading)

      return reading 

   def _readDirSizes(self, reading):

      if self._dirList:

         now = datetime.now()

         if self._dirLastCheckDate is None or int((now - self._dirLastCheckDate).total_seconds()) >= self._dirReadMinSeconds:
            self._dirCacheSizes = {}

            for d in self._dirList:
               self._dirCacheSizes[d] = get_dir_size(d)

            self._dirLastCheckDate = now

         reading.dir_sizes = self._dirCacheSizes

   def _readNetIfaces(self, reading):
  
      if self._netIfaces:

         net_ifaces = {}
         counters = psutil.net_io_counters(pernic=True)
         now = datetime.now()
         
         for i in self._netIfaces:

            if i in counters:

               for io in ['tp_net_in', 'tp_net_out']:

                  state_key = '{}_{}'.format(i, io)
                  counter = counters[i][IO_COUNTER[io]]
                  last_i_io = None if state_key not in self._netIfacesLast else self._netIfacesLast[state_key]
                  cur_state = None

                  if last_i_io and last_i_io < counter:
                     cur_state = round(
                        (counter - last_i_io)
                        / 1000 ** 2
                        / (now - self._ifacesLastCheckDate).total_seconds(),
                        3)
                
                  self._netIfacesLast[state_key] = counter
                  net_ifaces[state_key] = cur_state
                
         self._ifacesLastCheckDate = now
         reading.net_ifaces = net_ifaces




# call main
#if __name__ == '__main__':
#   sensor = SystemSensor(True, ["/var/log"])
#   d = sensor.readData()
#   print(d.getDict()) 
