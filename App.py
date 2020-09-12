import os,sys,time,logging
from datetime import date
from PIL import Image, ImageDraw, ImageFont

from EpdDisplay import EpdDisplay
from Weather import Weather
from WData import WData

# Logging
logging.basicConfig(filename="messages.log",level=logging.DEBUG)

logging.info("\nStarting pi_thermo App")

# Feature: zoom
# - one x-value for each 5 minutes
# - zoom in
# - zoom out: per 10 minutes, 20 minutes, etc
# - (eventually will span days and maybe weeks)
# - File spans 1 week of data
# - maximum zoom out: 1 week (so that at most 2 files must be loaded)

# Feature: time on x-axis (bottom)
# -4 hr
# -1 day
# etc

# Feature: y-axis ticks
# .1, .2, .5, 1, 2, 5, 10, 20, 50, 100, 200, 500, etc.
# maximum # of ticks up to 8

# In order to support zoom (which I would like to), data needs to be time-associated
# - numpy array
# - get list of spacing (finite differences) between time values
# - use finite differences to decide on where "joined" segments become breaks
# - assign x-value associated with each time
# - prepare all possible x-values, either leaving None or averaging duplicates
# - create groups of joined segments according to gaps
def plot_data(draw, x, pos, size, minspan=5):
  (px,py) = pos
  (w,h) = size
  draw.line((px+opts.axis_width,py,px+opts.axis_width,py+h),fill=0)
  for i in range(0,int((w-opts.axis_width)/5)):
    draw.point((px+opts.axis_width+5*i,py+h/2),fill=0)
  # TODO zoom
  logging.debug("Plot size: {} x {}".format(w,h))
  logging.debug("{} data [{}-{}]".format(w-opts.axis_width,len(x)-(w-opts.axis_width),len(x)))
  if w > opts.axis_width:
    x2 = x[max(len(x)-(w-opts.axis_width),0):len(x)]
  else:
    x2 = []
 
  x2_trim = list(filter(lambda y: y is not None,x2))
  if len(x2_trim)>0:
    minx = min(x2_trim)
    maxx = max(x2_trim)
    meanx = (maxx+minx)/2
    spanx = maxx-minx
    if spanx < minspan:
      maxx = meanx + minspan/2
      minx = meanx - minspan/2
    points = []
    for i in range(len(x2)):
      if x2[i] is None:
        if len(points)>0:
          draw.line(points,fill=0)
        points = []
      else:
        voffset = (x2[i] - minx) / (maxx - minx)
        points.append((px+opts.axis_width+i,py+h*(1-voffset)))
    if len(points)>0:
      draw.line(points,fill=0)
    draw.text((px,py),"{:.0f}".format(maxx),font=font_small,fill=0)
    draw.text((px,py+h-10),"{:.0f}".format(minx),font=font_small,fill=0)

class opts:
  # Timing
  numx = 30     # probes per measurement
  timx = 5.0*60 # seconds per measurement
  disx = 1      # measurements per display update

  # Drawing options
  text_length = 75 # hspace for current readings on left
  fsize = 16       # size of current readings font
  fsize_small = 10 # size of axis label font

  plot_gap = 5     # vspace between blots
  axis_width = 15   # space for tick labels beside plot

font = ImageFont.truetype('fonts/SourceSansPro-Regular.ttf', opts.fsize)
font_small = ImageFont.truetype('fonts/SourceSansPro-Regular.ttf', opts.fsize_small)

class App:
  def __init__(self):
    self.edisplay = EpdDisplay()
    self.w = Weather()
    self.wdata = WData()

  def read(self,file="data.csv"):
    logging.info("Reading data from {}".format(file))
    if os.path.exists(file):
      self.wdata.read(file)
    else:
      logging.info("No data to load")

  def write(self,wdata,file="data.csv"):
    wdata.write(file,append=True,last=True)

  def pad(self,n=5):
    self.wdata.store(None,None,None,None)

  def draw(self):
    def getLast(x):
      xl = list(filter(lambda y: y is not None,x))
      if len(xl) > 0: return xl[-1]
      return None
    img = self.edisplay.sizedImage()
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    plot_width = width - opts.text_length
    plot_height = (height-4*opts.plot_gap)/3
    
    font_offset = (plot_height-opts.fsize)/2

    temx = self.wdata.temperature
    humx = self.wdata.humidity
    prex = self.wdata.pressure

    logging.debug("Lengths:")
    logging.debug("  tem:{}".format(len(temx)))
    logging.debug("  hum:{}".format(len(humx)))
    logging.debug("  pre:{}".format(len(prex)))

    tem = getLast(temx)
    hum = getLast(humx)
    pre = getLast(prex)

    tem = 0 if tem is None else tem
    hum = 0 if hum is None else hum
    pre = 0 if pre is None else pre

    draw.text((5, font_offset+opts.plot_gap), "T:  {:.1f}°".format(tem), font = font, fill = 0)
    draw.text((5, font_offset+2*opts.plot_gap + plot_height), "H:  {:.1f}%".format(hum), font = font, fill = 0)
    draw.text((5, font_offset+3*opts.plot_gap + 2*plot_height), "P: {:.2f}".format(pre), font = font, fill = 0)

    plot_data(draw, temx, (opts.text_length,opts.plot_gap), (plot_width,plot_height), 2)
    plot_data(draw, humx, (opts.text_length,2*opts.plot_gap+plot_height), (plot_width,plot_height), 5)
    plot_data(draw, prex, (opts.text_length,3*opts.plot_gap+2*plot_height), (plot_width,plot_height), 1)

    self.edisplay.display(img)
    del draw
    del img

  # 3 threads: probe, display, buttons (interaction)? Can I interupt on gpio?
  def probe(self):
    logging.info("Beginning probe")
    t0 = 0
    while True:
      wdata2 = WData()
      for i in range(opts.numx): # number of averages
        logging.debug(".")
        wdata2.store(t0,self.w.get_temperature(),self.w.get_humidity(),self.w.get_pressure())
        time.sleep(opts.timx/opts.numx)
      self.wdata.store(t0,*wdata2.get_means())
      if not t0 % opts.disx:
        self.draw()
        self.write(wdata2)
      del wdata2
      t0 += 1
      logging.debug("Time: {}".format(t0))

app = App()
app.read()
app.pad()
app.probe()
