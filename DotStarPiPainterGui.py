#!/usr/bin/python3

# --------------------------------------------------------------------------
# DotStar Light Painter for Raspberry Pi.
#
# Hardware requirements:
# - Raspberry Pi computer (any model)
# - DotStar LED strip (any length, but 144 pixel/m is ideal):
#   www.adafruit.com/products/2242
# - Five momentary pushbuttons for controls, such as:
#   www.adafruit.com/products/1010
# - One 74AHCT125 logic level shifter IC:
#   www.adafruit.com/products/1787
# - High-current, high-capacity USB battery bank such as:
#   www.adafruit.com/products/1566
# - Perma-Proto HAT for Raspberry Pi:
#   www.adafruit.com/products/2310
# - Various bits and bobs to integrate the above parts.  Wire, Perma-Proto
#   PCB, 3D-printed enclosure, etc.  Your approach may vary...improvise!
#
# Software requirements:
# - Raspbian "Lite" operating system
# - Python 3
# - Adafruit Blinka Python library (CircuitPython for Raspberry Pi),
#   including DotStar module.
#   learn.adafruit.com/circuitpython-on-raspberrypi-linux
#   learn.adafruit.com/adafruit-dotstar-leds/python-circuitpython
# - usbmount:
#   sudo apt-get install usbmount
#   See file "99_lightpaint_mount" for add'l info.
#
# Written by Phil Burgess / Paint Your Dragon for Adafruit Industries.
#
# Adafruit invests time and resources providing this open source code,
# please support Adafruit and open-source hardware by purchasing products
# from Adafruit!
# --------------------------------------------------------------------------
import os
#import signal
import board
import busio
import digitalio
import adafruit_dotstar as dotstar
#import adafruit_fancyled.adafruit_fancyled as fancy
#import adafruit_fancyled.fastled_helpers as helper
#import bluetooth
import time
from evdev import InputDevice, ecodes
from lightpaint import LightPaint
from PIL import Image
from PIL import ImageFont

#import SH1106
#import config
#import traceback
#import RPi.GPIO as GPIO

#from luma.core.interface.serial import i2c
#from luma.core.render import canvas
#from luma.oled.device import sh1106
#from demo_opts import get_device

#serial = i2c(port=1, address=0x3c)
#device = sh1106(serial, rotate=2)

#import subprocess



# CONFIGURABLE STUFF -------------------------------------------------------

num_leds   = 373         # Length of LED strip, in pixels
#pin_go     = board.D13   # GPIO pin numbers for 'go' button,
#pin_next   = board.D26   # previous image, next image and speed +/-.
#pin_prev   = board.D5    # Buttons should connect from these pins to ground.
#pin_faster = board.D6
#pin_slower = board.D19
vflip      = 'false'      # 'true' if strip input at bottom, else 'false'
direct     = 'R > L'
order      = dotstar.BGR # BGR for current DotStars, GBR for pre-2015 strips
order2     = 'bgr'       # lightpaint lib uses a different syntax for same
spispeed   = 12000000    # SPI clock rate...
# 12000000 (12 MHz) is the fastest I could reliably operate a 288-pixel
# strip without glitching. You can try faster, or may need to set it lower,
# no telling.

# DotStar strip data & clock connect to hardware SPI0 pins (GPIO 10 & 11)
#!!! SPI1 (GPIO 20 & 21).
strip     = dotstar.DotStar(board.SCK_1, board.MOSI_1, num_leds, brightness=1.0,
              auto_write=False, pixel_order=order)
# The DotStar library is used for status updates (loading progress, etc.),
# we pull shenanigans here and also access the SPI bus directly for ultra-
# fast strip updates with data out of the lightpaint library.
spi       = busio.SPI(board.SCK_1, MOSI=board.MOSI_1)
path_usb  = '/media/usb'         # USB stick mount point
path      = '/home/pi/pictures'  # path to images
#mousefile = '/dev/input/mouse0'  # Mouse device (as positional encoder)
#eventfile = '/dev/input/event0'  # Mouse events accumulate here
dev       = None                 # None unless mouse is detected

gamma          = (2.8, 2.8, 2.8) # Gamma correction curves for R,G,B
color_balance  = (128, 255, 180) # Max brightness for R,G,B (white balance)
power_value    = 1450
power_settings = (power_value, power_value + 100)    # Battery avg and peak current
brightness_val = 1.0

# INITIALIZATION -----------------------------------------------------------

# Clear display.
#disp.clear()

# Create blank image for drawing.
#image1 = Image.new('1', (disp.width, disp.height), "WHITE")
#draw = ImageDraw.Draw(image1)
#font = ImageFont.truetype('Font.ttf', 20)
#font2 = ImageFont.truetype('Font.ttf', 12)
font2 = ImageFont.load_default()

# Set control pins to inputs and enable pull-up resistors.
# Buttons should connect between these pins and ground.
# button_go               = digitalio.DigitalInOut(pin_go)
# button_go.direction     = digitalio.Direction.INPUT
# button_go.pull          = digitalio.Pull.UP
# button_prev             = digitalio.DigitalInOut(pin_prev)
# button_prev.direction   = digitalio.Direction.INPUT
# button_prev.pull        = digitalio.Pull.UP
# button_next             = digitalio.DigitalInOut(pin_next)
# button_next.direction   = digitalio.Direction.INPUT
# button_next.pull        = digitalio.Pull.UP
# button_slower           = digitalio.DigitalInOut(pin_slower)
# button_slower.direction = digitalio.Direction.INPUT
# button_slower.pull      = digitalio.Pull.UP
# button_faster           = digitalio.DigitalInOut(pin_faster)
# button_faster.direction = digitalio.Direction.INPUT
# button_faster.pull      = digitalio.Pull.UP

ledBuf = bytearray(4 + (num_leds * 4) + ((num_leds + 15) // 16))
for i in range(4):
    ledBuf[i] = 0x00 # 4 header bytes
for i in range(4 + num_leds * 4, len(ledBuf)):
    ledBuf[i] = 0xFF # Footer bytes
imgNum     = 0    # Index of currently-active image
duration   = 5.0  # Image paint time, in seconds
filename   = [] # List of image files (nothing loaded yet)
lightpaint = None # LightPaint object for currently-active image (none yet)
repeat     = 1    # Repetition
delay      = 0
countdown  = 0    # Time to wait


# FUNCTIONS ----------------------------------------------------------------
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def color_fill(color, wait):
    strip.fill(color)
    strip.show()
    time.sleep(wait)

def rainbow_cycle(wait):
   # strip.brightness(0.1)
    for j in range(255):
        for i in range(75):
            rc_index = (i * 256 // num_leds) + j
            strip[5*i] = wheel(rc_index & 255)
        strip.show()
        time.sleep(wait)

# Signal handler when SIGUSR1 is received (USB flash drive mounted,
# triggered by usbmount and 99_lightpaint_mount script).
def sigusr1_handler(signum, frame):
    scanfolder(path)

# Ditto for SIGUSR2 (USB drive removed -- clears image file list)
def sigusr2_handler(signum, frame):
    global filename
    filename = None
    imgNum   = 0
    # Current LightPaint object is left resident

# Scan root folder of USB drive for viable image files.
def scanfolder(chemin):
    global imgNum, filename
    files     = os.listdir(chemin)
    num_files = len(files) # Total # of files, whether images or not
    filename  = []         # Filename list of valid images
    imgNum    = 0
    if num_files == 0:
        return
    for i, f in enumerate(files):
        lower =  i      * num_leds // num_files
        upper = (i + 1) * num_leds // num_files
        for n in range(lower, upper):
            strip[n] = (0, 0, 5) 
        strip.show()
        if f[0] == '.':
            continue
        try:
            Image.open(os.path.join(chemin, f))
        except:
            continue       # Is directory or non-image file; skip
        filename.append(f) # Valid image, add to list
        time.sleep(0.05)   # Tiny pause so progress bar is visible
    strip.fill(0)
    strip.show()
    if len(filename) > 0:              # Found some image files?
        filename.sort()                # Sort list alphabetically
  #      lightpaint = loadImage(path,imgNum, power_settings, vflip, direct) # Load first image

# Load image, do some conversion and processing as needed before painting.
def loadImage(path,index,power_var,vflip_var,direct_var):
    num_images = len(filename)
    lower      =  index      * num_leds // num_images
    upper      = (index + 1) * num_leds // num_images
    #for n in range(lower, upper):
    #    strip[n] = (1, 0, 0) # Red = loading
    #strip.show()
    print("Loading '" + filename[index] + "'...\n")

    #client_sock.send("Loading '" + filename[index] + "'...\n")
    startTime = time.time()
    # Load image, convert to RGB if needed
    img = Image.open(os.path.join(path, filename[index])).convert("RGB")

    #print('\t%dx%d pixels' % img.size)

    # If necessary, image is vertically scaled to match LED strip.
    # Width is NOT resized, this is on purpose.  Pixels need not be
    # square!  This makes for higher-resolution painting on the X axis.
    if img.size[1] != num_leds:
        #print('\tResizing...',)
        img = img.resize((img.size[0], num_leds), Image.LANCZOS)
        #print('now %dx%d pixels' % img.size)
    if direct_var == 'L > R':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    # Convert raw RGB pixel data to a 'bytes' buffer.
    # The C module can easily work with this format.
    pixels = img.tobytes() # Current/preferred PIL method
    #print('\t%f seconds' % (time.time() - startTime))

    # Do external C processing on image; this provides 16-bit gamma
    # correction, diffusion dithering and brightness adjustment to
    # match power source capabilities.
    #for n in range(lower, upper):
    #    strip[n] = (0, 0, 1) 
    #strip.show()
    #print('Processing...')
    startTime  = time.time()
    # Pixel buffer, image size, gamma, color balance and power settings
    # are REQUIRED arguments.  One or two additional arguments may
    # optionally be specified:  "order='rgb'" is to maintain compat.
    # (color reordering is done in DotStar lib now)
    # "vflip='true'" indicates that the
    # input end of the strip is at the bottom, rather than top (I
    # prefer having the Pi at the bottom as it provides some weight).
    # Returns a LightPaint object which is used later for dithering
    # and display.
    lightpaint = LightPaint(pixels, img.size, gamma, color_balance,
      power_var, order=order2, vflip=vflip_var)
    #print('\t%f seconds' % (time.time() - startTime))

    # Success!
    #for n in range(lower, upper):
    #    strip[n] = (0, 1, 0) # Green
    #strip.show()
    #time.sleep(0.25) # Tiny delay so green 'ready' is visible
    print('Ready!')

    strip.fill(0)
    strip.show()
    return lightpaint
def infoImage(index):
    img = Image.open(os.path.join(path, filename[index])).convert("RGB")
    width, height = img.size
    return (width,height)



#def btn():
#    if not button_go.value:     return 1
#    if not button_faster.value: return 2
#    if not button_slower.value: return 3
#    if not button_next.value:   return 4
#    if not button_prev.value:   return 5
#    return 0

# BLUETOOTH ---------------------------------------------------------------
#hostMACAddress = 'B8:27:EB:7E:85:27'
#server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
#server_sock.bind((hostMACAddress, bluetooth.PORT_ANY))
#server_sock.listen(1)

#port = server_sock.getsockname()[1]
#print("Waiting for connection on RFCOMM channel %d" % port)

#client_sock,address = server_sock.accept()
#print("Accepted connection from ",address)


# def btn():
#   #  while True:
#   #  data = client_sock.recv(1024)
#   #  data = data.decode()  # byte used by python3
#  ##   client_sock.close()
#  ##   server_sock.close()
#     #    if not data: break
#     data=9
#     if (button_go.value==False): return 1    # go
#     #    if (data=="1"): return 1    # go
#     if (button_faster.value==False): return 10    # faster  
#     if (button_slower.value==False): return 11    # slower
#     if (button_next.value==False): return 12    # next
#     if (button_prev.value==False): return 13    # prev
#     if (data=="6"): return 6    # fill all
#     if (data=="7"): return 7    # brightness up
#     if (data=="8"): return 8    #  
#     if (data=="q"):
#         os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
#         exit()    # prev
#     if (data=="s"): # clean shutdown
#         os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
#         os.system("sudo shutdown -h now")
#     if (data=="r"): # reboot
#         os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
#         os.system("sudo shutdown -r now")
#     return 0

# MAIN LOOP ----------------------------------------------------------------

# Init some stuff for speed selection...
max_time    = 10.0
min_time    =  0.1
time_range  = (max_time - min_time)
speed_pixel = int(num_leds * (duration - min_time) / time_range)
duration    = min_time + time_range * speed_pixel / (num_leds - 1)
prev_btn    = 0
rep_time    = 0.1

scanfolder(path) # USB drive might already be inserted
lightpaint = loadImage(path,imgNum, power_settings, vflip, direct) # Load first image

#signal.signal(signal.SIGUSR1, sigusr1_handler) # USB mount signal
#signal.signal(signal.SIGUSR2, sigusr2_handler) # USB unmount signal

# while False:
#     try:
#         b = btn()
#         if b == 1 and lightpaint != None:
#             # Paint!
#             time.sleep(coutdown) # attente
#             spi.try_lock()
#             spi.configure(baudrate=spispeed)

#             if dev is None: # Time-based

#                 startTime = time.time()
#                 while True:
#                     t1      = time.time()
#                     elapsed = t1 - startTime
#                     if elapsed > duration:
#                         break
#                     # dither() function is passed a destination buffer and
#                     # a float from 0.0 to 1.0 indicating which column of
#                     # the source image to render.  Interpolation happens.
#                     lightpaint.dither(ledBuf, elapsed / duration)
#                     spi.write(ledBuf)

#             else: # Encoder-based

#                 mousepos = 0
#                 scale    = 0.01 / (speed_pixel + 1)
#                 while True:
#                     input = epoll.poll(-1) # Non-blocking
#                     for i in input: # For each pending...
#                         try:
#                             for event in dev.read():
#                                 if(event.type == ecodes.EV_REL and
#                                    event.code == ecodes.REL_X):
#                                     mousepos += event.value
#                         except:
#                             # If this occurs, usually power settings
#                             # are too high for battery source.
#                             # Voltage sags, Pi loses track of USB device.
#                             print('LOST MOUSE CONNECTION')
#                             continue

#                     pos = abs(mousepos) * scale
#                     if pos > 1.0: break
#                     lightpaint.dither(ledBuf, pos)
#                     spi.write(ledBuf)

#           #  if btn() != 1: # Button released?
#             strip.fill(0)
#             strip.show()
#           #  spi.unlock()

#         elif b == 2:
#             # Decrease paint duration
#             if speed_pixel > 5:
#                 speed_pixel -= 5
#                 duration = (min_time + time_range *
#                   speed_pixel / (num_leds - 1))
#                 strip[speed_pixel] = (0, 0, 128)
#                 strip.show()
#                 startTime = time.time()
#                 while ((time.time() - startTime) < rep_time): continue
#                 strip.fill(0)
#                 strip.show()
#         elif b == 3:
#             # Increase paint duration (up to 10 sec maximum)
#             if speed_pixel < num_leds - 6:
#                 speed_pixel += 5
#                 duration = (min_time + time_range *
#                   speed_pixel / (num_leds - 1))
#                 strip[speed_pixel] = (0, 0, 128)
#                 strip.show()
#                 startTime = time.time()
#                 while ((time.time() - startTime) < rep_time): continue
#                # while (btn() == 3 and ((time.time() - startTime) < rep_time)): continue
#                 strip.fill(0)
#                 strip.show()
#         elif b == 4 and filename != None:
#             # Next image (if USB drive present)
#             imgNum += 1
#             if imgNum >= len(filename): imgNum = 0
#             lightpaint = loadImage(imgNum)
#             # while btn() == 4: continue
#         elif b == 5 and filename != None:
#             # Previous image (if USB drive present)
#             imgNum -= 1
#             if imgNum < 0: imgNum = len(filename) - 1
#             lightpaint = loadImage(imgNum)
#             # while btn() == 5: continue
#         elif b == 6:
#             print("rainbow")
#             startTime = time.time()
#             while True:
#                 t1      = time.time()
#                 elapsed = t1 - startTime
#                 if elapsed > duration:
#                     strip.fill(0)
#                     strip.show()
#                     break
#                 rainbow_cycle(0)
#         elif b == 7: # Increase brightness
#             if power_value < 1550:
#                 power_value += 72.5
#             else:
#                 power_value = 72.5
#             power_settings = (int(power_value), int(power_value) + 100)    # Battery avg and peak current
#             print(power_value)
#             client_sock.send("Brightness: '" + str(round(power_value/1450*100,0)) + "%\n")
#             lightpaint = loadImage(imgNum)
#         elif b == 8: # Decrease brightness
#             if power_value > 50:
#                 power_value -= 72.5
#             else:
#                 power_value = 1450
#             power_settings = (int(power_value), int(power_value) + 100)    # Battery avg and peak current
#             print(power_value)
#             client_sock.send("Brightness: '" + str(round(power_value/1450*100,0)) + "%\n")
#             lightpaint = loadImage(imgNum) # Reload image with new brightness
#         if b > 0 and b == prev_btn:
#             # If button held, accelerate speed selection
#             rep_time *= 0.92
#             if rep_time < 0.01: rep_time = 0.01
#         else:
#             rep_time = 0.2
#         prev_btn = b

#     except KeyboardInterrupt:
#         os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
#         print('Cleaning up')
#         strip.fill(0)
#         strip.show()
#         print('Done!')
#         break

#     except bluetooth.btcommon.BluetoothError:
#         os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
#         print('Erreur BT')
#         client_sock,address = server_sock.accept()
#         print("Accepted connection from ",address)
#         os.system("echo 1 | sudo tee /sys/class/leds/led0/brightness")
#         continue