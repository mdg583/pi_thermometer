from lib.waveshare_epd import epd2in7

class EpdDisplay:
  epd = None

  def __init__(self):
    self.epd = epd2in7.EPD()  # get the display
    self.epd.init()           # initialize the display

  def sizedImage(self):
    return Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)

  def display(self, image):
    self.epd.Clear(0xFF)
    self.epd.display(self.epd.getbuffer(image))

  def get_width(self):
    return epd2in7.EPD_HEIGHT

  def get_height(self):
    return epd2in7.EPD_WIDTH