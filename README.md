# tempmqtt

MQTT System and Temperature sensor for DHT22 and BME280

## Installation

```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

## Configuration

```
cp example.config.yml config.yml
```

1. update broker and topic
2. configure readings section

Sections system and temperature, should be configured if specified in the readings

**Note:** for temperature, specify which sensor to use *bme280* or *dht22* in *temperature.use*

## Sample config

```
broker:
  address: '192.168.0.35'
  port: 1883
  ttl: 60
  topic: 'ha/sensor/test/topic'

readings:
- system
#- temperature

temperature:

  # use bme280 or dht22 and check respective sensor configuration section below
  use: bme280
  
  # if file name specified, a text file will be created with sensor data, useful for embedding in images
  #txt: 'last_reading.txt'

  sensors:
    bme280:
      i2c_address: 0x76
      i2c_bus: 1
    dht22:
      gpio: 22

system:
   # will read RPI specific values
   is_pi: false
   
   path_size:
   - /var/log
   
   size_refresh_rate: 600

round_digitis: 1
sleep_secs: 60
```
