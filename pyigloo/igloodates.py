import re
from datetime import datetime
from dateutil.tz import tzoffset
import pytz

"""
Igloo dates are formatted like: /Date(1646832169387-0500)/
The format is /Date( TIMESTAMP TIMEZONE )
"""

class date:

    def __init__ (self, timestamp):
        self.utc = pytz.UTC
        self.raw = timestamp
        if m := re.match(r"\/Date\(([0-9]+)([+-][0-9]{4})\)", timestamp):
            self.timestamp = m.group(1)
            self.timezone = m.group(2)
            d = datetime.fromtimestamp(int(self.timestamp)/1000)
            self.datetime = datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, tzinfo=tzoffset(None, int(m.group(2))*6*6))
            self.utc = self.datetime.astimezone(self.utc).replace(tzinfo=None)

    def __str__(self):
        return self.datetime.strftime("%c")

