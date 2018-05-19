
import TempSensor
from TempSensor import Reading
from bme280 import bme280


class BME280Sensor(TempSensor.TempSensor):
   def __init__(self, I2C_ADDRESS = 0x76, I2C_BUS = 1):
      self.lastReading = None
      self.roundDigits = 1
      
      bme280.bme280_i2c.set_default_i2c_address(int(str(I2C_ADDRESS), 0))
      bme280.bme280_i2c.set_default_bus(int(I2C_BUS))
      bme280.setup()
      
      
   def readBME280ID():
      # Chip ID Register Address
      REG_ID = 0xD0
      return bme280.bme280_i2c.default_bus.read_i2c_block_data(bme280.bme280_i2c.default_i2c_address, REG_ID, 2)


      
   def readData(self):
      data_all = bme280.read_all()
      if data_all is None:
         return False
      
      if self.lastReading is None:
         self.lastReading = Reading()
      
      self.lastReading.humidity = data_all.humidity
      self.lastReading.temperature = data_all.temperature
      self.lastReading.pressure = data_all.pressure
      return True

      
   def parseData(self, reading = Reading()):
      if self.lastReading is not None:
         reading.humidity = round(self.lastReading.humidity, self.roundDigits)
         reading.temperature = round(self.lastReading.temperature, self.roundDigits)
         reading.pressure = round(self.lastReading.pressure, self.roundDigits)
         return reading
      
      return None