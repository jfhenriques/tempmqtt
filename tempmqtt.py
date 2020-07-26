
#
#  pip3 install psutil
#  pip3 install paho-mqtt
#  pip3 install tzlocal
#
#


import paho.mqtt.client as mqtt
from time import sleep
from datetime import datetime
#from DHT22Sensor import DHT22Sensor
#from BME280Sensor import BME280Sensor
from Reading import ReadingGroup
from pprint import pprint
from TempSensorReading import TempSensor, TempReading
from SystemReading import SystemSensor

ROUND_DIGITS = 1
DHT22_GPIO = 22

BME280_I2C_ADDRESS = 0x76
BME280_I2C_BUS = 1

broker_ha = '192.168.0.35'
broker_ha_port = 1883
broker_ha_ttl = 60

mqtt_temp_topic = 'ha/sensor/test/topic'
sleep_secs = 60

last_reading_file = 'last_reading.txt'


client = mqtt.Client()

def write_file(file, t = 'N/A', h = 'N/A', p = None):
   try:
      f = open(file, 'w')
   except:
      print_ts('Cannot open {}'.format(arg))
   else:
      if p is not None:
         f.write("T: {}°C  H: {}%  hPa: {}".format(t, h, p))
      else:
         f.write("T: {}°C  H: {}%".format(t, h))
      f.close()





def print_ts(msg):
   ts = datetime.now()
   print("[{}] {}".format(ts, msg), flush=True)



def on_connect(client, userdata, flags, rc):
   print_ts("Connected with result code {}".format(rc))

def mqtt_connect():
   client.on_connect = on_connect
   client.connect(broker_ha, broker_ha_port, broker_ha_ttl)
   client.loop_start()
   
   
def setup_dht22():
   sensor = DHT22Sensor(DHT22_GPIO)
   sensor.roundDigits = ROUND_DIGITS
   return sensor
   
def setup_bme280():
   sensor = BME280Sensor(BME280_I2C_ADDRESS, BME280_I2C_BUS)
   sensor.roundDigits = ROUND_DIGITS
   return sensor
   
   
def temp_read(sensor, readingGroup): 
   if not sensor.readData():
      print_ts("[ERROR] Could not get sensor readings...")

   else:
      tempReading = TempReading()
      if sensor.parseData(tempReading) is not None:
         #print_ts('Got reading: Temp={0:0.1f}*  Humidity={1:0.1f}%  Pressure={2:0.1f}hPa'.format(reading.temperature, reading.humidity, reading.pressure))
         readingGroup.registerReading(tempReading)
        
         try:
            write_file(last_reading_file, tempReading.temperature, tempReading.humidity, tempReading.pressure)
         except:
            pass
         
         else:
            print_ts("[ERROR] Temperature Reading doesn't have an acceptable quality...")

def system_read(sensor, readingGroup): 
      sysReading = sensor.readData()
      readingGroup.registerReading(sysReading)


def main():
   sleep(2) 
   print_ts('Connecting to broker...')
   mqtt_connect()
   #tempSensor = setup_dht22()
   #tempSensor = setup_bme280()
   systemSensor = SystemSensor(True, ["/var/log"], 600)

   print_ts('Starting loop...')

   while True:

      readingGroup = ReadingGroup()
      
      # Fetch temperature data
      #temp_read(tempSensor, readingGroup)


      # Check System Readings
      system_read(systemSensor, readingGroup)
      

      # Check if there are readings to publish
      if readingGroup.hasReadings():
         client.publish(mqtt_temp_topic, readingGroup.toJSON())

      else:
         print_ts("[WARN] No Readings to publish")

      sleep(sleep_secs)


# call main 
if __name__ == '__main__': 
   main()  

