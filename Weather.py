class Weather:
  def __init__(self,sea_level_pressure=1013.25):
    i2c = busio.I2C(board.SCL, board.SDA)
    self.bmp280 = adafruit_bmp280b.Adafruit_BMP280_I2C(i2c,0x76)
    self.bmp280.sea_level_pressure = sea_level_pressure
    self.dhtDevice = adafruit_dht.DHT22(board.D4)

  def get_temperature(self):
    try:
      t1 = self.bmp280.temperature
    except Exception as e:
      print(str(e))
      t1 = None
    try:
      t2 = self.dhtDevice.temperature
    except Exception as e:
      print(str(e))
      t2 = None
    if t1 is None and t2 is None:
      return None
    elif t1 is None:
      return t2
    elif t2 is None:
      return t1
    else:
      return (t1 + t2)/2

  def get_pressure(self):
    try:
      return self.bmp280.pressure
    except:
      return None

  def get_humidity(self):
    try:
      return self.dhtDevice.humidity
    except:
      return None

  def get_altitude(self):
    try:
      return self.bmp280.altitude
    except:
      return None