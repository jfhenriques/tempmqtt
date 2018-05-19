
import paho.mqtt.client as mqtt
from time import sleep
import json
import datetime
import tzlocal
from DHT22Sensor import DHT22Sensor


ROUND_DIGITS = 1
DHT22_GPIO = 22

broker_ha = '192.168.1.14'
broker_ha_port = 1883
broker_ha_ttl = 60

mqtt_temp_topic = 'ha/sensor/pi3balcony/temperature'
sleep_secs = 2

last_reading_file = 'last_reading.txt'



client = mqtt.Client()

def write_file(file, t, h):
   try:
      f = open(file, 'w')
   except:
      print_ts('Cannot open {}'.format(arg))
   else:
      f.write("Temp: {}°C  Hum: {}%".format(t, h))
      f.close()





def print_ts(msg):
   ts = datetime.datetime.now()
   print("[{}] {}".format(ts, msg), flush=True)



def on_connect(client, userdata, flags, rc):
   print_ts("Connected with result code {}".format(rc))

def mqtt_connect():
   client.on_connect = on_connect
   client.connect(broker_ha, broker_ha_port, broker_ha_ttl)
   client.loop_start()
   
   
def setup_dht22():
   sensor = DHT22Sensor(DHT22_GPIO)
   sensor.round_dig = ROUND_DIGITS
   return sensor

def main(): 
   print_ts('Connecting to broker...')
   mqtt_connect()
   sensor = setup_dht22()

   print_ts('Starting loop...')

   while True:
      
      
      if not sensor.readData():
         print_ts("[ERROR] Could not get sensor readings...")

      else:
         reading = sensor.parseData()
       
         if reading is not None:
            now = datetime.datetime.now(tzlocal.get_localzone())
            print_ts('Got reading: Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(reading.temp, reading.hum))
            data = {'temperature': reading.temp, 'humidity': reading.hum, 'timestamp': now.isoformat()}
            client.publish(mqtt_temp_topic, json.dumps(data))
            try:
               write_file(last_reading_file, reading.temp, reading.hum)
            except:
               pass
      
            sleep(sleep_secs)
            
         else:
            print_ts("[ERROR] Readings don't have acceptable quality...")
        
# call main 
if __name__ == '__main__': 
   main()  
