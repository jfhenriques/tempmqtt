
#
#  pip3 install psutil
#  pip3 install paho-mqtt
#  pip3 install tzlocal
#
#


import paho.mqtt.client as mqtt
from time import sleep
from datetime import datetime
from Reading import ReadingGroup
from pprint import pprint
from TempSensorReading import TempSensor, TempReading
from SystemReading import SystemSensor
import yaml


last_reading_file = None


client = None
cfg = None

def write_file(file, t = 'N/A', h = 'N/A', p = None):
   try:
      f = open(file, 'w')
   except:
      print_error('Cannot open {}'.format(arg))
   else:
      if p is not None:
         f.write("T: {}°C  H: {}%  hPa: {}".format(t, h, p))
      else:
         f.write("T: {}°C  H: {}%".format(t, h))
      f.close()


def print_ts(msg):
   ts = datetime.now()
   print("[{}] {}".format(ts, msg), flush=True)

def print_error(msg):
   print_ts("[ERROR] {}".format(msg))


def on_connect(client, userdata, flags, rc):
   print_ts("Connected with result code {}".format(rc))

def mqtt_connect():
   client.on_connect = on_connect
   client.connect(cfg['broker']['address'], cfg['broker']['port'], cfg['broker']['ttl'])
   client.loop_start()                     
   
   
def setup_dht22():
   from DHT22Sensor import DHT22Sensor
   gpio = None
   try:
     gpio = cfg['temperature']['sensors']['dht22']['gpio']
   except:
      print_error('Please define gpio in temperature.sensors.dht22 config')
      quit()

   sensor = DHT22Sensor(gpio)
   sensor.roundDigits = 1 if not 'round_digitis' in cfg else cfg['round_digitis']
   return sensor
   
def setup_bme280():
   from BME280Sensor import BME280Sensor
   i2c_address = None
   i2c_bus = None
   try:
     i2c_address = cfg['temperature']['sensors']['bme280']['i2c_address']
     i2c_bus = cfg['temperature']['sensors']['bme280']['i2c_bus']
   except:
      print_error('Please define i2c_address and i2c_bus in temperature.sensors.bme280 config')
      quit()

   sensor = BME280Sensor(i2c_address, i2c_bus)
   sensor.roundDigits = 1 if not 'round_digitis' in cfg else cfg['round_digitis']
   return sensor


def setup_system():
   is_pi = False if not 'is_pi' in cfg['system'] else cfg['system']['is_pi']
   path_size = [] if not 'path_size' in cfg['system'] else cfg['system']['path_size']
   size_refresh_rate = 600 if not 'size_refresh_rate' in cfg['system'] else cfg['system']['size_refresh_rate']
   net_ifaces = [] if not 'net_ifaces' in cfg['system'] else cfg['system']['net_ifaces']

   return SystemSensor(is_pi, net_ifaces, path_size, size_refresh_rate)
 
   
def temp_read(sensor, readingGroup): 
   if not sensor.readData():
      print_error("Could not get sensor readings...")

   else:
      tempReading = TempReading()
      if sensor.parseData(tempReading) is not None:
         #print_ts('Got reading: Temp={0:0.1f}*  Humidity={1:0.1f}%  Pressure={2:0.1f}hPa'.format(reading.temperature, reading.humidity, reading.pressure))
         readingGroup.registerReading(tempReading)
        
         if last_reading_file is not None:
            try:
               write_file(last_reading_file, tempReading.temperature, tempReading.humidity, tempReading.pressure)
            except:
               pass
         
      else:
         print_error("Temperature Reading doesn't have an acceptable quality...")

def system_read(sensor, readingGroup): 
   sysReading = sensor.readData()
   readingGroup.registerReading(sysReading)


def main():

   global cfg
   global client
   global last_reading_file

   try:
      cfg = yaml.load(open('config.yml', 'r'), Loader=yaml.FullLoader)
   except:
      print_eror("Please create config.yml file")
      return

   if 'readings' not in cfg or not isinstance(cfg['readings'], list):
      print_error('Please define readings section in config')
      return

   if 'broker' not in cfg or 'address' not in cfg['broker'] or 'port' not in cfg['broker'] or 'topic' not in cfg['broker'] or 'ttl' not in cfg['broker']:
      print_error('Please define broken section in config with elements: address, port, topic and ttl')
      return

   sleep_secs = 60 if not 'sleep_secs' in cfg else cfg['sleep_secs']
   mqtt_topic = cfg['broker']['topic']
   
   tempSensor = None
   systemSensor = None
   
   validSensors = 0

   for s in cfg['readings']:

      if s == 'temperature' and 'temperature' in cfg and 'use' in cfg['temperature']:

         if 'txt' in cfg['temperature']:
            last_reading_file = cfg['temperature']['txt']
            

         if cfg['temperature']['use'] == 'bme280':
            print_ts("Setting up sensor: bme280")
            tempSensor = setup_bme280()
            validSensors += 1

         elif cfg['temperature']['use'] == 'dht22':
            print_ts("Setting up sensor: dht22")
            tempSensor = setup_dht22()
            validSensors += 1

      elif s == 'system' and 'system' in cfg:
         print_ts("Setting up sensor: system")
         systemSensor = setup_system()
         validSensors += 1

   if validSensors <= 0:
      print_error('Readings or respective configuration sections not properly configured')
      return

   print_ts('Connecting to broker...')
   client = mqtt.Client()
   mqtt_connect()

   print_ts('Starting loop...')

   while True:

      readingGroup = ReadingGroup()
      
      # Fetch temperature data
      if tempSensor is not None:
         temp_read(tempSensor, readingGroup)


      # Check System Readings
      if systemSensor is not None:
         system_read(systemSensor, readingGroup)
      

      # Check if there are readings to publish
      if readingGroup.hasReadings():
         client.publish(mqtt_topic, readingGroup.toJSON())

      else:
         print_ts("[WARN] No readings to publish")
      
      sleep(sleep_secs)


# call main 
if __name__ == '__main__': 
   main()  

