# tempmqtt

MQTT System and Temperature (DHT22 or BME280) sensors

## Installation

```bash
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

**Note:** in case temperature sensors is going to be used (development boards onlu, like raspberry pi), uncoment the 3 first lines in the requirements.txt before installing

## Configuration

```bash
cp example.config.yml config.yml
```

1. update broker and topic
2. configure readings section

Sections system and temperature, should be configured if specified in the readings

**Note:** for temperature, specify which sensor to use *bme280* or *dht22* in *temperature.use*

## Sample config

```yaml
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
   # Read basic metrics: cpu, memory, etc
   read_basic: True

   # will read RPI specific values
   is_pi: false
   
   path_size:
   - /var/log

   size_refresh_rate: 600

   net_ifaces:
   - eth0

round_digitis: 1
sleep_secs: 60
```

## Example json data sent to the broker
```json
{
    "timestamp": "2020-05-23T16:30:03.218322+01:00",
    "system": {
        "processor_use": 0,
        "last_boot": "2020-07-29T16:30:03+01:00",
        "cpu_temperature": 50.5,
        "memory_use_percent": 14.1,
        "dir_sizes": {
            "/var/log": 15676
        },
        "throttled": "0",
        "load_15": 0.0,
        "disk_use_percent": 25.0,
        "load_5": 0.0,
        "swap_use_percent": 1.0,
        "net_ifaces": {
            "eth0_tp_net_out": 0.002,
            "eth0_tp_net_in": 0.001
        }
    },
    "temperature": {
        "pressure": 1001.1,
        "humidity": 65.1,
        "temperature": 22.3
    }
}
```

