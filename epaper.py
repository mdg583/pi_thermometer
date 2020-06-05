import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
  sys.path.append(libdir)
else:
  sys.exit("Can't find lib")

#import logging
from waveshare_epd import epd2in7
from PIL import Image, ImageDraw, ImageFont

epd = epd2in7.EPD()  # get the display
epd.init()           # initialize the display

bangers_font = ImageFont.truetype('fonts/Bangers-Regular.ttf', 30)

def printToDisplay(string,x=25,y=65):
  HBlackImage = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)  # 255: clear the frame
  # Create draw object and pass in the image layer we want to work with (HBlackImage)
  draw = ImageDraw.Draw(HBlackImage)
  font = bangers_font
  draw.text((x, y), string, font = font, fill = 0)
  epd.Clear(0xFF)
  epd.display(epd.getbuffer(HBlackImage))

printToDisplay("Hello, World!",10,65)