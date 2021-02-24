# -*- coding:utf-8 -*-
#imports 
import spidev as SPI
import ST7789
import gpiozero as GPIO
import datetime
import time
import subprocess
import sys
import os
import DotStarPiPainterGui as dot
import animation1 as ani
from PIL import Image,ImageDraw,ImageFont
#import bluetooth
#import bluetoothDot as bluet

bluetoothStatus = 'off'
b = 0
level = 0
mem = 0
SCNTYPE = 1 # 1= OLED #2 = TERMINAL MODE BETA TESTS VERSION
iterate = 'OFF'

# Load default font.
#font = ImageFont.load_default()
font = ImageFont.truetype("/home/pi/python3/Tahoma.ttf", 25, encoding="unic")
font2 = ImageFont.truetype("/home/pi/python3/Tahoma.ttf", 60, encoding="unic")
font3 = ImageFont.truetype("/home/pi/python3/Tahoma.ttf", 120, encoding="unic")
fonta = ImageFont.truetype("/home/pi/python3/fontawesome-regular.ttf", 25, encoding="unic")

color1 = 'yellow'
color2 = 'black'
color3 = 'cyan'
color4 = 'blue'

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 240
height = 240
image = Image.new('1', (width, height))
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
line1 = top
line2 = top+30
line3 = top+60
line4 = top+90
line5 = top+120
line6 = top+150
line7 = top+180
line8 = top+210
brightness = 1 #LCD brightness
fichier=""
# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 24
bus = 0 
device = 0

# 240x240 display with hardware SPI:
device = ST7789.ST7789(SPI.SpiDev(bus, device),RST, DC, BL)

# Initialize library.
device.Init()

# Clear display.
device.clear()

#GPIO define and LCD configuration
KEY_UP_PIN     = GPIO.Button(6)  #stick up
KEY_DOWN_PIN   = GPIO.Button(19) #stick down
KEY_LEFT_PIN   = GPIO.Button(5) #5  #sitck left // go back
KEY_RIGHT_PIN  = GPIO.Button(26) #stick right // go in // validate
KEY_PRESS_PIN  = GPIO.Button(13) #stick center button
KEY1_PIN       = GPIO.Button(17)#21 #key 1 // up
KEY2_PIN       = GPIO.Button(27)#20  #20 #key 2 // cancel/goback
KEY3_PIN       = GPIO.Button(22)#16 #key 3 // down
LCD            = GPIO.PWMOutputDevice(24, initial_value=brightness)
buttonState    = 1 #etat du bouton
lastButtonState= 0 #variable pour l'état précédent du bouton poussoir

yoyo = False
DIR_VALUE = ['R > L', 'L > R', 'Yoyo']
VERTICAL_VALUE = ['false','true']
INCREMENT_VALUE = ['OFF','ON']

def DisplayText(l1,l2,l3,l4,l5,l6,l7,l8):
    # simple routine to display 7 lines of text
    if SCNTYPE == 1:
        image1 = Image.new("RGB", (device.width, device.height), color2)
        draw = ImageDraw.Draw(image1)
        if True:
            draw.text((0, line1), l1, font=font, fill=color1)
            draw.text((0, line2), l2, font=font, fill=color1)
            draw.text((0, line3), l3, font=font, fill=color1)
            draw.text((0, line4), l4, font=font, fill=color1)
            draw.text((0, line5), l5, font=font, fill=color1)
            draw.text((0, line6), l6, font=font, fill=color1)
            draw.text((0, line7), l7, font=font, fill=color1)
            draw.text((0, line8), l8, font=font, fill=color1)
            
            if page == 0 and curseur != 0:
                draw.line([(5,line2),(235,line2)],fill=color1, width=2, joint=None)
            if 0 == l1.find('>',0,1):
                l1 = l1.replace(">"," ",1)
                draw.rectangle((0, 0, 240, 28), outline=None, width=0, fill=color4)
                draw.text((0, line1), l1, font=font, outline=0,fill="white")
            if 0 == l2.find('>',0,1):
                l2 = l2.replace(">"," ",1)
                draw.rectangle((0, 30, 240, 58), outline=None, width=0, fill=color4)
                draw.text((0, line2), l2, font=font, outline=0,fill="white")
            if 0 == l3.find('>',0,1):
                l3 = l3.replace(">"," ",1)
                draw.rectangle((0, 60, 240, 88), outline=None, width=0, fill=color4)
                draw.text((0, line3), l3, font=font, outline=0,fill="white")
            if 0 == l4.find('>',0,1):
                l4 = l4.replace(">"," ",1)
                draw.rectangle((0, 90, 240, 118), outline=None, width=0, fill=color4)
                draw.text((0, line4), l4, font=font, outline=0,fill="white")
            if 0 == l5.find('>',0,1):
                l5 = l5.replace(">"," ",1)
                draw.rectangle((0, 120, 240, 148), outline=None, width=0, fill=color4)
                draw.text((0, line5), l5, font=font, outline=0,fill="white")
            if 0 == l6.find('>',0,1):
                l6 = l6.replace(">"," ",1)
                draw.rectangle((0, 150, 240, 178), outline=None, width=0, fill=color4)
                draw.text((0, line6), l6, font=font, outline=0,fill="white")
            if 0 == l7.find('>',0,1):
                l7 = l7.replace(">"," ",1)
                draw.rectangle((0, 180, 240, 208), outline=None, width=0, fill=color4)
                draw.text((0, line7), l7, font=font, outline=0,fill="white")
            if 0 == l8.find('>',0,1):
                l8 = l8.replace(">"," ",1)
                draw.rectangle((0, 210, 240, 238), outline=None, width=0, fill=color4)
                draw.text((0, line8), l8, font=font, outline=0,fill="white")

        device.ShowImage(image1,0,0)
    if SCNTYPE == 2:
        os.system('clear')

def DisplayFile(l1,l2,l3,l4,l5,l6,l7,l8):
    top = -2
    # simple routine to display 7 lines of text
    if SCNTYPE == 1:
        image1 = Image.new("RGB", (device.width, device.height), color2)
        icon = chr(0xf114)
        icon2 = chr(0xf115) #open
        icon3 = chr(0xf03e) #image
        draw = ImageDraw.Draw(image1)
        for li in [l1,l2,l3,l4,l5,l6,l7,l8]:
            if 0 == li.find('>',0,1):
                draw.rectangle((0, top, 240, top+28), outline=None, width=0, fill=color4)
            if -1 != li.find('*'):
                if -1!=li.find('>',0,1):
                    draw.text((0, top), icon2, font=fonta, fill=color1)
                else:
                    draw.text((0, top), icon, font=fonta, fill=color1)
                li = li.replace('*','   ')
            else:
                li = '   '+li
                #draw.text((0, top), icon3, font=fonta, fill=color1)
            if -1 != li.find('>'):
                li = li.replace('>',' ',1)            
            draw.text((0, top), li, font=font, outline=0,fill=color1)
            top+=30
        device.ShowImage(image1,0,0)
    if SCNTYPE == 2:
        os.system('clear')



def folder_icon(x,y):
    draw.line([(x,y),(x,y+26)],fill=color1, width=1, joint=None)
    draw.line([(x,y+26),(x+30,y+26)],fill=color1, width=1, joint=None)
def switch_menu(argument):
    if dot.countdown == 0:
        val1 = 'OFF'
    else:
        val1 = str(dot.countdown)
    if dot.vflip == 'false':
        val2 = 'OFF'
    else:
        val2 = 'ON'
    switcher = {
        0: "_"+os.path.splitext(dot.filename[dot.imgNum])[0]+" >", #display name file whitout ext
        1: "_BRIGHTNESS  "+str(int(dot.power_value/1450*100)) +"%",
        2: "_SPEED             "+str(round(dot.duration))+" s",
        3: "_COUNTDOWN   "+val1+" s",
        4: "_DIRECTION     "+dot.direct,
        5: "_VERT. FLIP       "+val2,        
        6: "_ADVANCED",
        7: "_OPTIONS",  #fin menu principal
        8: "_FILE INFO",
        9: "_REPEAT              "+str(dot.repeat),
        10: "_REPEAT TIME    "+str(dot.delay)+" s",
        11: "_INCREMENT      "+iterate,
        12: "_DEMO",
        13: "_",
        14: "_",
        15: "_",
        16: "_LCD BRIGHT. "+str(int(brightness*100)) +"%",
        17: "_DISPLAY OFF",
        18: "_KEYS TEST",
        19: "_RESTART GUI",
        20: "_EXIT GUI",
        21: "_SYSTEM SHUTDOWN",
        22: "_BLUETOOTH",
        23: "_ABOUT",
        24: "_COLORCYCLE",
        25: "_RAINBOW",
        26: "_SPARKLE",
        27: "_MAGENTA",
        28: "_RAINBOW SPARKLE",
        29: "_RAINBOW 2",
        30: "_",
        31: "_",
        32: "_",
        33: "_",
        34: "_",
        35: "_",
        36: "_",
        37: "_",
        38: "_",
        39: "_",
        40: "_",
        41: "_",
        42: "_",
        43: "_",
        44: "_",
        45: "_",
        46: "_",
        47: "_",
        48: "_"
}
    return switcher.get(argument, "Invalid")
def about():
    # simple sub routine to show an About
    DisplayText(
        "",
        "Pi Light Paint",
        "Pizero ",
        "V 1.1 02/2021",
        "",
        "dbriand77@gmail.com",
        "",
        ""
        )
    while not KEY_LEFT_PIN.is_pressed:
        #wait
        menu = 1
    page = 0
def LCDContrast(contrast):
    #set contrast 0 to 1
    if SCNTYPE == 1:
        while not KEY_LEFT_PIN.is_pressed:
            #loop until press left to quit
            #with canvas(device) as draw:
            if True:
                image1 = Image.new("RGB", (device.width, device.height), color2)
                draw = ImageDraw.Draw(image1)
                if not KEY_UP_PIN.is_pressed: # button is released
                        draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=color1)  #Up filled
                        if contrast<1:
                            contrast += 0.1
                if not KEY_DOWN_PIN.is_pressed: # button is released
                        draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=color1) #down filled
                        if contrast>0.2:
                            contrast -= 0.1
                draw.text((10, 1), 'LCD CONTRAST',  font=font, fill=color1)
                draw.line([(5,35),(235,35)],fill=color1, width=3, joint=None)
                draw.text((80, 82), str(int(contrast*100)) +"%",  font=font2, fill=color1)
                device.ShowImage(image1,0,0)
                LCD.value=contrast
    return(contrast)
def stickBrightness(powerBrightness):
    #set contrast 0 to 255
    if SCNTYPE == 1:
        while not KEY_LEFT_PIN.is_pressed:
            #loop until press left to quit
            #with canvas(device) as draw:
            if True:
                image1 = Image.new("RGB", (device.width, device.height), color2)
                draw = ImageDraw.Draw(image1)
                if not KEY_UP_PIN.is_pressed: # button is released
                        draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=color1)  #Up filled
                        if powerBrightness < 1550:
                            powerBrightness += 14.5
                        else:
                            powerBrightness = 14.5
                        #time.sleep(0.02)
                if not KEY_DOWN_PIN.is_pressed: # button is released
                        draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=color1) #down filled
                        if powerBrightness > 20:
                            powerBrightness -= 14.5
                        else:
                            powerBrightness = 1450
                        #time.sleep(0.02)
                draw.text((10, 1), 'BRIGHTNESS',  font=font, fill=color1)
                draw.line([(5,35),(235,35)],fill=color1, width=3, joint=None)
                draw.text((80, 82), str(int(powerBrightness/1450*100)) +"%",  font=font2, fill=color1)
                device.ShowImage(image1,0,0)
    return(powerBrightness)
def increment(val_inc,name):
    #set increment 0 to 100
    if SCNTYPE == 1:
        while not KEY_LEFT_PIN.is_pressed:
            #loop until press left to quit
            #with canvas(device) as draw:
            if True:
                image1 = Image.new("RGB", (device.width, device.height), color2)
                draw = ImageDraw.Draw(image1)
                if not KEY_UP_PIN.is_pressed: # button is released
                        draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=color1)  #Up filled
                        val_inc +=  1
                        if val_inc>100:
                            val_inc = 100
                        time.sleep(0.1)
                if not KEY_DOWN_PIN.is_pressed: # button is released
                        draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=color1) #down filled
                        val_inc -= 1
                        if val_inc<0:
                            val_inc = 0
                        time.sleep(0.1)
                draw.text((10, 1), name,  font=font, fill=color1)
                draw.line([(5,35),(235,35)],fill=color1, width=3, joint=None)
                draw.text((100, 85), str(int(round(val_inc))),  font=font2, fill=color1)
                device.ShowImage(image1,0,0)
    return(val_inc)
def status(val_inc,list,name):
    #set increment 0 to 100
    #[1,2,3].index(2) # => 1
    if SCNTYPE == 1:
        a = list.index(val_inc)
        while not KEY_LEFT_PIN.is_pressed:
            #loop until press left to quit
            #with canvas(device) as draw:
            image1 = Image.new("RGB", (device.width, device.height), color2)
            draw = ImageDraw.Draw(image1)
            if not KEY_UP_PIN.is_pressed: # button is released
                draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=0)  #Up
            else: # button is pressed:
                draw.polygon([(100, 80), (120, 50), (140, 80)], outline=color1, fill=color1)  #Up filled
                a +=  1
                if a > len(list)-1:
                    a = 0
                time.sleep(0.1)
            if not KEY_DOWN_PIN.is_pressed: # button is released
                draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=0) #down
            else: # button is pressed:
                draw.polygon([(140, 160), (120, 190), (100, 160)], outline=color1, fill=color1) #down filled
                a -= 1
                if a < 0:
                    a = len(list)-1
                time.sleep(0.1)
            draw.text((10, 1), name,  font=font, fill=color1)
            draw.line([(5,35),(235,35)],fill=color1, width=3, joint=None)
            draw.text((70, 85), list[a],  font=font2, fill=color1)
            device.ShowImage(image1,0,0)
    return(list[a])
def splash(folder,image):
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), folder, image))
    splash = Image.open(img_path)
    wpercent = (device.height/float(splash.size[1]))
    wsize = int((float(splash.size[0])*float(wpercent)))
    if wsize < device.width:
        c = (-device.width+wsize)/2
    else:
        c = 1
    splash = splash.resize((wsize, device.height), Image.BILINEAR) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, c, 0, 1, 0), Image.BILINEAR) #\.convert(device.mode)    
    device.ShowImage(splash,0,0)
    time.sleep(2) #2 secondes splash screen
def SreenOFF():
    #put screen off until press left
    if SCNTYPE == 1:
        while not KEY_LEFT_PIN.is_pressed:
            LCD.off()
            time.sleep(0.1)
        LCD.on()
def KeyTest():
    if SCNTYPE == 1:
        while not KEY_LEFT_PIN.is_pressed:
           # with canvas(device) as draw:
           if True:
                image1 = Image.new("RGB", (device.width, device.height), color2)
                draw = ImageDraw.Draw(image1)
                if not KEY_UP_PIN.is_pressed: # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=color1, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=color1, fill=color1)  #Up filled

                if not KEY_LEFT_PIN.is_pressed: # button is released
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=color1, fill=0)  #left
                else: # button is pressed:
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=color1, fill=color1)  #left filled

                if not KEY_RIGHT_PIN.is_pressed: # button is released
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=color1, fill=0) #right
                else: # button is pressed:
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=color1, fill=color1) #right filled

                if not KEY_DOWN_PIN.is_pressed: # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=color1, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=color1, fill=color1) #down filled

                if not KEY_PRESS_PIN.is_pressed: # button is released
                        draw.rectangle((20, 22,40,40), outline=color1, fill=0) #center 
                else: # button is pressed:
                        draw.rectangle((20, 22,40,40), outline=color1, fill=color1) #center filled

                if not KEY1_PIN.is_pressed: # button is released
                        draw.ellipse((70,0,90,20), outline=color1, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,0,90,20), outline=color1, fill=color1) #A button filled

                if not KEY2_PIN.is_pressed: # button is released
                        draw.ellipse((100,20,120,40), outline=color1, fill=0) #B button
                else: # button is pressed:
                        draw.ellipse((100,20,120,40), outline=color1, fill=color1) #B button filled
                        
                if not KEY3_PIN.is_pressed: # button is released
                        draw.ellipse((70,40,90,60), outline=color1, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,40,90,60), outline=color1, fill=color1) #A button filled
                device.ShowImage(image1,0,0)
def FileSelect(chemin,pos):
    global mem, level, lastButtonState, buttonState
    maxi=len(dot.filename) #number of records
    ligne = ["","","","","","","",""]
    time.sleep(0.1) #wait a little to navigate
    #directories = glob.glob(path+"/*/")
    directories = [ f.name for f in os.scandir(chemin) if f.is_dir() ]
    if level != 0:
        directories.insert(0, '..')
    subfolders = len(directories)
    maxi+=subfolders
    cur=pos+subfolders
    mem = pos
    arrow = ['*'+item if item != '..' else item for item in directories]
    allfiles = arrow + dot.filename
    while not KEY_LEFT_PIN.is_pressed:
        #on boucle
        tok=0
        if maxi < 9:
            for n in range(0,8):
                if n<maxi:
                    if n == cur:
                        ligne[n] = ">"+os.path.splitext(allfiles[n])[0]
                    else:
                        ligne[n] = " "+os.path.splitext(allfiles[n])[0]
                else:
                    ligne[n] = ""
        else:
            if cur+8<maxi:
                for n in range (cur,cur + 8):
                    if n == cur:
                        ligne[tok] = ">"+os.path.splitext(allfiles[n])[0]
                    else:
                        ligne[tok] = " "+os.path.splitext(allfiles[n])[0]
                    tok=tok+1
            else:
                for n in range(maxi-8,maxi):
                    if n == cur:
                        ligne[tok] = ">"+os.path.splitext(allfiles[n])[0]
                    else:
                        ligne[tok] = " "+os.path.splitext(allfiles[n])[0]                            
                    tok=tok+1
        if not KEY_UP_PIN.is_pressed: # button is released
            menu = 1
        else: # button is pressed:
            cur = cur -1
            if cur<0:
                cur = maxi-1
        if not KEY_DOWN_PIN.is_pressed: # button is released
            menu = 1
        else: # button is pressed:
            cur = cur + 1
            if cur>maxi-1:
                cur = 0
        if not KEY_RIGHT_PIN.is_pressed: # button is released
            lastButtonState = 0
            menu = 1
        elif lastButtonState == 0: # buttonState != lastButtonState : # button is pressed:
            #lightpaint = loadImage(cur)
            if cur > subfolders-1:
                mem = cur - subfolders
                splash(chemin,allfiles[cur])
                return(chemin,mem)
            else:
                if directories[cur] == '..':
                    level-=1
                else:
                    level+=1
                #print("level:"+str(level))
                dot.path=chemin+"/"+directories[cur]
                dot.scanfolder(dot.path)
                lastButtonState = 1
                FileSelect(dot.path,0)
                return(dot.path,mem)
        DisplayFile(ligne[0],ligne[1],ligne[2],ligne[3],ligne[4],ligne[5],ligne[6],ligne[7])
        #time.sleep(0.04)
    return(chemin,pos)
def restart():
    #cmd="sudo -u pi bash -c python3 /home/pi/python3/gui.py > /home/pi/log.txt 2>&1"
    #exe = subprocess.check_output(cmd, shell = True )
    #print("argv was",sys.argv)
    #print("sys.executable was", sys.executable)
    DisplayText(
    "",
    "",
    "",
    "RESTART NOW...",
    "",
    "",
    "",
    ""
    )
    os.execv(sys.executable, ['python3'] + sys.argv)
    return()  
def btn():
 #   while True:
    data = client_sock.recv(1024)
    data = data.decode()  # byte used by python3
 #   client_sock.close()
 #   server_sock.close()
 #       if not data: break
    print(data)
    if (data=="1"): return 1    # go
    if (data=="2"): return 2    # faster  
    if (data=="3"): return 3    # slower
    if (data=="4"): return 4    # next
    if (data=="5"): return 5    # prev
    if (data=="6"): return 6    # fill all
    if (data=="7"): return 7    # brightness
    if (data=="8"): return 8     
    return 0
#init vars 
curseur = 0
page=0  
menu = 1
ligne = ["","","","","","","",""]
selection = 0
if SCNTYPE == 1:
    splash('images','splash.jpg')  # display boot splash image ---------------------------------------------------------------------
    # light off the led
    os.system("echo none | sudo tee /sys/class/leds/led0/trigger")
    os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
while 1:
    if bluetoothStatus == 'on': b=btn()
    if not KEY_UP_PIN.is_pressed: # button is released
        menu = 1
    else: # button is pressed:
        curseur -= 1
        if curseur<0:
            curseur = 7     
    if not KEY_LEFT_PIN.is_pressed: # button is released
        menu = 1
    else: # button is pressed:
                # back to main menu on Page 0
        page = 0
        curseur = 0    
    if not KEY_RIGHT_PIN.is_pressed: # button is released
        menu = 1
    else: # button is pressed:
        selection = 1
        lastButtonState = 1
    if not KEY_DOWN_PIN.is_pressed: # button is released
        menu = 1
    else: # button is pressed:
        curseur += 1
        if curseur>7:
            curseur = 0
    if not KEY_PRESS_PIN.is_pressed or 1 == b: # button is released
        menu = 1
    else: # button PRESS is pressed:
        if dot.lightpaint != None:
            # Paint!
            # DisplayText(
            #                 "",
            #                 "",
            #                 "",
            #                 "    PAINT!",
            #                 "",
            #                 "",
            #                 ""
            #                 )
            compteur = dot.countdown
            while compteur:
                image1 = Image.new("RGB", (device.width, device.height), color2)
                draw = ImageDraw.Draw(image1)
                draw.text((90, 50), str(compteur),  font=font3, fill=color3)
                device.ShowImage(image1,0,0)
                compteur-=1
                time.sleep(1)

            #time.sleep(dot.countdown) # attente
            LCD.off()
            dot.spi.try_lock()
            dot.spi.configure(baudrate=dot.spispeed)
            for i in range(0,dot.repeat): 
            #if dev is None: # Time-based
                startTime = time.time()
                while True:
                    t1      = time.time()
                    elapsed = t1 - startTime
                    if elapsed > dot.duration:
                        break
                    # dither() function is passed a destination buffer and
                    # a float from 0.0 to 1.0 indicating which column of
                    # the source image to render.  Interpolation happens.
                    dot.lightpaint.dither(dot.ledBuf, elapsed / dot.duration)
                    dot.spi.write(dot.ledBuf)
                if dot.repeat > 1:
                    if dot.delay > 0:
                        dot.strip.fill(0)
                        dot.strip.show()
                    time.sleep(dot.delay)
                if yoyo:
                    if dot.direct == 'R > L':
                        dot.direct = 'L > R'
                    else:
                        dot.direct = 'R > L'
                    dot.lightpaint = dot.loadImage(dot.path,dot.imgNum, dot.power_settings, dot.vflip, dot.direct)
                dot.strip.fill(0)
                dot.strip.show()
            dot.spi.unlock()
            if iterate == 'ON':
                dot.imgNum+=1
                dot.lightpaint = dot.loadImage(dot.path,dot.imgNum, dot.power_settings, dot.vflip, dot.direct)  
            LCD.on()
    #-----------
    if selection == 1:
        # une option du menu a ete validee on va calculer la page correspondante
            if page == 24:
                #demo menu with dotstar
                RED = (64, 0, 0)
                YELLOW = (64, 37, 0)
                ORANGE = (64, 10, 0)
                GREEN = (0, 64, 0)
                TEAL = (0, 64, 30)
                CYAN = (0, 64, 64)
                BLUE = (0, 0, 64)
                PURPLE = (45, 0, 64)
                MAGENTA = (64, 0, 5)
                WHITE = (32, 32, 32)
                BLACK = (0,0,0)
                if curseur == 0:
                    #colorcycle
                    while not KEY_LEFT_PIN.is_pressed:
                        ani.colorcycle.animate()
                    dot.color_fill(BLACK, 1)
                if curseur == 1:
                    #rainbow
                    while not KEY_LEFT_PIN.is_pressed:
                        ani.rainbow.animate()
                    dot.color_fill(BLACK, 1)
                if curseur == 2:
                    #sparkle
                    while not KEY_LEFT_PIN.is_pressed:
                        ani.sparkle.animate()
                    dot.color_fill(BLACK, 1)
                if curseur == 3:
                    #fill magenta
                    while not KEY_LEFT_PIN.is_pressed:
                        ani.solid.animate()
                    dot.color_fill(BLACK, 1)
                if curseur == 4:
                    #rainbow sparkle
                    while not KEY_LEFT_PIN.is_pressed:
                        ani.rainbow_sparkle.animate()
                    dot.color_fill(BLACK, 1)
                if curseur == 5:
                    #rainbow 2
                    startTime = time.time()
                    while not KEY_LEFT_PIN.is_pressed:
                        # t1      = time.time()
                        # elapsed = t1 - startTime
                        # if elapsed > dot.duration:
                        #     dot.strip.fill(0)
                        #     dot.strip.show()
                        #     break
                        dot.rainbow_cycle(0)
                    dot.color_fill(BLACK, 1)
            if page == 8:
                #advanced menu
                if curseur == 0:
                    #file info
                    (width, height) = dot.infoImage(dot.imgNum)
                    longueur = (width / 250) * (373 / height)
                    DisplayText(
                    "File name:  ",
                    dot.filename[dot.imgNum],
                    '',
                    'Real size:',
                    '%d x %d px' %(width, height),
                    "Real lenght: "+str(round(longueur,1))+" m",
                    "",
                    ""
                    )
                    while not KEY_LEFT_PIN.is_pressed:
                        #wait
                        menu = 1
                if curseur == 1:
                    #repeat image 
                    dot.repeat=increment(dot.repeat, 'REPEAT IMAGE')
                if curseur == 2:
                    #time between image
                    dot.delay=increment(dot.delay, 'TIME')
                if curseur == 3:
                    iterate = status(iterate, INCREMENT_VALUE, 'INCREMENT')
                    menu=1       
                if curseur == 4:
                    page = 24
                    curseur = 0                    
            if page == 16:
                #options menu
                if curseur == 0: brightness = LCDContrast(brightness)
                if curseur == 1: SreenOFF()
                if curseur == 2: KeyTest()
                if curseur == 3: restart()
                if curseur == 4:
                    os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
                    exit()
                if curseur == 5:
                    DisplayText(
                        "",
                        "",
                        "",
                        "SHUTDOWN NOW...",
                        "",
                        "",
                        "",
                        ""
                        )
                    time.sleep(0.5)
                    DisplayText("","","","","","","","")
                    LCD.off()
                    device.clear()
                    cmd="sudo shutdown 0"
                    exe = subprocess.check_output(cmd, shell = True )
                    while not KEY_LEFT_PIN.is_pressed:
                        #wait
                        menu = 1
                if curseur == 6:
                    menu = 1
                    #bluetooth
                    #os.system("echo 0 | sudo systemctl enable bluetooth")

                    # BLUETOOTH ---------------------------------------------------------------
                    #hostMACAddress = 'B8:27:EB:7E:85:27'
                    #server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
                    #server_sock.bind((hostMACAddress, bluetooth.PORT_ANY))
                    #1server_sock.listen(1)

                    #port = server_sock.getsockname()[1]
                    #print("Waiting for connection on RFCOMM channel %d" % port)

                    #client_sock,address = server_sock.accept()
                    #print("Accepted connection from ",address)

                    #bluetoothStatus = 'on'
                if curseur == 7: about()
            if page == 0:
            #main menu
                if curseur == 0:
                    (dot.path,dot.imgNum) = FileSelect(dot.path,dot.imgNum)
                    dot.lightpaint = dot.loadImage(dot.path,dot.imgNum, dot.power_settings, dot.vflip, dot.direct)
                if curseur == 1:
                    #brightness
                    dot.power_value = stickBrightness(dot.power_value)
                    dot.power_settings = (int(dot.power_value), int(dot.power_value) + 100)    # Battery avg and peak current
                    dot.lightpaint = dot.loadImage(dot.path,dot.imgNum, dot.power_settings, dot.vflip, dot.direct) # Reload image with new brightness loadImage(index,power_var,vflip_var,direct_var)
                if curseur == 2:
                    #speed
                    dot.duration = increment(dot.duration,'SPEED')
                if curseur == 3:
                    #countdown
                    dot.countdown = increment(dot.countdown,'COUNTDOWN')
                if curseur == 4:
                    dot.direct = status(dot.direct,DIR_VALUE,'DIRECTION')
                    if dot.direct == 'Yoyo':
                        yoyo = True
                        dot.direct = 'R > L'
                    else:
                        yoyo = False
                    dot.lightpaint = dot.loadImage(dot.path,dot.imgNum, dot.power_settings, dot.vflip, dot.direct)                                    
                if curseur == 5:
                    dot.vflip = status(dot.vflip,VERTICAL_VALUE,'VERTICAL FLIP')
                    dot.lightpaint = dot.loadImage(dot.path,dot.imgNum, dot.power_settings, dot.vflip, dot.direct)              
                if curseur == 6:
                    #advanced menu
                    page = 8
                    curseur = 0
                if curseur == 7:
                    #option menu
                    page = 16
                    curseur = 0
    ligne[0]=switch_menu(page)
    ligne[1]=switch_menu(page+1)
    ligne[2]=switch_menu(page+2)
    ligne[3]=switch_menu(page+3)
    ligne[4]=switch_menu(page+4)
    ligne[5]=switch_menu(page+5)
    ligne[6]=switch_menu(page+6)
    ligne[7]=switch_menu(page+7)
    #add curser on front on current selected line
    for n in range(0,8):
        if page+curseur == page+n:
            if page == 1:
                if readCapacity(bus) < 16:
                    ligne[n] = ligne[n].replace("_","!")
                else:
                    ligne[n] = ligne[n].replace("_",">",1)
            else:
                ligne[n] = ligne[n].replace("_",">",1)
        else:
            ligne[n] = ligne[n].replace("_"," ")
    DisplayText(ligne[0],ligne[1],ligne[2],ligne[3],ligne[4],ligne[5],ligne[6],ligne[7])
    #print(page+curseur) #debug trace menu value
    #time.sleep(0.04)
    selection = 0
