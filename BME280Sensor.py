
from TempSensorReading import *
from bme280 import bme280


class BME280Sensor(TempSensor):
   def __init__(self, I2C_ADDRESS = 0x76, I2C_BUS = 1):
      self.lastReading = None
      self.roundDigits = 1
      self.humidity_hist = None
      self.temperature_hist = None
      self.pressure_hist = None
      self.history_size = 5
      self.historyReading = None
      
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
         self.lastReading = TempReading()
      
      self.lastReading.humidity = data_all.humidity
      self.lastReading.temperature = data_all.temperature
      self.lastReading.pressure = data_all.pressure
      return True

      
   def parseData(self, reading = None):
      if self.lastReading is not None:
      
         if self.historyReading is None:
            self.historyReading = TempReading()
      
         self.historyReading.humidity = calculate_res_mean(self.historyReading.humidity, self.lastReading.humidity, self.history_size)
         self.historyReading.temperature = calculate_res_mean(self.historyReading.temperature, self.lastReading.temperature, self.history_size)
         self.historyReading.pressure = calculate_res_mean(self.historyReading.pressure, self.lastReading.pressure, self.history_size)
         
         if reading is None:
            reading = TempReading()
            
         reading.humidity = round(self.historyReading.humidity, self.roundDigits)
         reading.temperature = round(self.historyReading.temperature, self.roundDigits)
         reading.pressure = round(self.historyReading.pressure, self.roundDigits)
         return reading
      
      return None
