
from datetime import datetime
import tzlocal
import json

class ReadingGroup():
   def __init__(self):
      self.readings = {}
      self._hasReadings = False

   def registerReading(self, reading):
      self.readings[reading.getReadingName()] = reading.getDict()
      self._hasReadings = True

   def hasReadings(self):
      return self._hasReadings

   def toJSON(self, timestamp = True):
      self.readings['timestamp'] = datetime.now(tzlocal.get_localzone()).isoformat() if timestamp else None
      
      return json.dumps(self.readings)


class Reading:
   def __init__(self):
      pass

   def getReadingName(self):
      pass
      
   def getDict(self):
      pass

