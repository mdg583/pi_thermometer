import os,csv

class WData:
  def __init__(self):
    self.time        = []
    self.temperature = []
    self.humidity    = []
    self.pressure    = []

  def store(self, time, temp, hum, pres):
    self.time.append(time)
    self.temperature.append(temp)
    self.humidity.append(hum)
    self.pressure.append(pres)

  def extend(self, wdata):
    self.time.extend(wdata.time)
    self.temperature.extend(wdata.temperature)
    self.humidity.extend(wdata.humidity)
    self.pressure.extend(wdata.pressure)

  def get_means(self, include_time=False):
    ti = []
    for i in range(len(self.time)):
      if self.time[i] is not None:
        ti.append(i)
    n = len(ti)
    
    def meanlist(x):
      r = 0
      n = 0
      for i in ti:
        if x[i] is not None:
          r += x[i]
          n += 1
      if n == 0: return None
      return r / n
    if include_time:
      return (self.time[ti[0]], meanlist(self.temperature), meanlist(self.humidity), meanlist(self.pressure))
    else:
      return (meanlist(self.temperature), meanlist(self.humidity), meanlist(self.pressure))

  def read(self, file):
    def str2val(val):
      if val=="": return None
      return float(val)
    with open(file, "r") as f:
      reader = csv.DictReader(f, delimiter=',', quotechar='\"')
      for row in reader:
        if "time" in row and "temperature" in row and "humidity" in row and "pressure" in row:
          self.time.append(str2val(row["time"]))
          self.temperature.append(str2val(row["temperature"]))
          self.humidity.append(str2val(row["humidity"]))
          self.pressure.append(str2val(row["pressure"]))
        else:
          raise Exception("csv must have columns: time, temperature, humidity, pressure")
  
  def write(self, file, append=False, last=False):
    # missing values
    def valstr(val):
      if val is None: return ""
      return str(val)
    # Does the file exists?
    fieldnames = ['time','temperature','humidity','pressure']
    write_header = not append or not os.path.exists(file)
    ftype = "a+" if append and os.path.exists(file) else "w+"
    with open(file, ftype) as f:
      writer = csv.DictWriter(f, delimiter=',', quotechar='\"', fieldnames=fieldnames)
      if write_header: writer.writeheader()
      if last:
        r = [len(self.time)-1]
      else:
        r = range(len(self.time))
      for i in r:
        row = {
          'time': valstr(self.time[i]),
          'temperature': valstr(self.temperature[i]),
          'humidity': valstr(self.humidity[i]),
          'pressure': valstr(self.pressure[i])
        }
        writer.writerow(row)

# w = WData()
# w.store(255,14,23,54)
# w.store(260,12,26,52)
# w.write("test.csv")
# w = WData.read("test.csv")
# w.write("test2.csv")
