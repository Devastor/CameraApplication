#Libraries
import pynmea2
import xlsxwriter

import RPi.GPIO as GPIO
#import time
import picamera
from PIL import Image
from time import sleep
import curses 
import sys, select, os
from datetime import datetime
from datetime import timedelta
from shutil import copyfile

import serial
import string
from pygame import mixer

#import pygtk
#pygtk.require('2.0')
import gtk
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 8 #25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


GPIO.setwarnings(False)
sleep (2)
port = "/dev/ttyAMA0"

ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)

MAX_UF = 33

start_time = datetime.now()

#Adress of USB_FLASH: /media/pi/8FAT

# returns the elapsed milliseconds since the start of the program
def millis():
   dt = datetime.now() - start_time
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms

impulse = 0
nowTime = 0
now_imp = 0

curses.initscr()
win = curses.newwin(0, 0)

dx = 0
dy = 0
ov_width = 0
ov_height = 0

camera = picamera.PiCamera()

resX = 800
resY = 380
zoomVal = 1.0
zoomStep = 0.1
numShots = 0
lat = 0
lon = 0
overlay_now = "none"


catched = True
checker = True

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN, pull_up_down = GPIO.PUD_UP)#added pull_up_down

nowTime = millis() 

i = 0

class MainClass:
    # This callback method moves the button to a new position
    # in the Fixed container.

    def clicked_exit(self, widget):
        mixer.music.stop()
        workbook_linux.close()
        workbook_usb.close()
        camera.close()
        sys.exit()

    def clicked_capture(self, widget):
        #time.sleep(1)
        #camera.annotate_text = 'CAPTURING...'
        global numShots
        worksheet_linux.write(numShots+1, 0, str(numShots))
        worksheet_linux.write(numShots+1, 1, str(time.strftime("%d_%m_%Y")))
        worksheet_linux.write(numShots+1, 2, str(time.strftime("%H-%M-%S_")))
        worksheet_linux.write(numShots+1, 3, str(now_imp))
        worksheet_linux.write(numShots+1, 4, str(lat))
        worksheet_linux.write(numShots+1, 5, str(lon))
        #time.sleep(1)
        worksheet_usb.write(numShots+1, 0, str(numShots))
        worksheet_usb.write(numShots+1, 1, str(time.strftime("%d_%m_%Y")))
        worksheet_usb.write(numShots+1, 2, str(time.strftime("%H-%M-%S_")))
        worksheet_usb.write(numShots+1, 3, str(now_imp))
        worksheet_usb.write(numShots+1, 4, str(lat))
        worksheet_usb.write(numShots+1, 5, str(lon))
        #time.sleep(1)
        filename = 'snap' + str(numShots) + '_' + time.strftime("%H-%M-%S_") + time.strftime("%d_%m_%Y") + '.jpg'
        camera.capture('/home/pi/Desktop/Devastor_camera/images/' + filename)
        sleep(1)
        #source = 'images/' + filename
        #dest = '/home/pi/Desktop/Devastor_camera/test' + filename
        #'/media/pi/8FAT/' + filename
        #os.popen('cp ' + source + dest) 
        copyfile('/home/pi/Desktop/Devastor_camera/images/' + filename, '/media/pi/8FAT/' + filename)
        numShots += 1 

    def clicked_plus(self, widget):
        global zoomVal
        if (zoomVal > zoomStep*2):
            zoomVal -= zoomStep
        camera.zoom = (0, 0, zoomVal, zoomVal)

    def clicked_minus(self, widget):
        global zoomVal
        if (zoomVal < 1):
            zoomVal += zoomStep
        camera.zoom = (0, 0, zoomVal, zoomVal)

    

    def removeCurrentOverlay(self, ov_name):
        if (ov_name == "red"):
            camera.remove_overlay(pad_red)
        elif (ov_name == "orange"):
            camera.remove_overlay(pad_orange)
        elif (ov_name == "yellow"):
            camera.remove_overlay(pad_yellow)
        elif (ov_name == "green"):
            camera.remove_overlay(pad_green)
        elif (ov_name == "cyan"):
            camera.remove_overlay(pad_cyan)
        elif (ov_name == "blue"):
            camera.remove_overlay(pad_cyan)
        elif (ov_name == "violet"):
            camera.remove_overlay(pad_violet)

    def camera_overlay_init(self):
        global pad_red
        global pad_orange
        global pad_yellow
        global pad_green
        global pad_cyan
        global pad_blue
        global pad_violet
        
        global img_red
        global img_orange
        global img_yellow
        global img_green
        global img_cyan
        global img_blue
        global img_violet
        # init ALL overlays
        img_red = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_red.png')
        ov_width = img_red.size[0]
        ov_height = img_red.size[1]
        #pad_red = Image.new('RGBA', (ov_width, ov_height))
        #pad_red.paste(img_red, (0, 0), img_red)
        pad_red = Image.new('RGBA', (((img_red.size[0] + 31) // 32) * 32, ((img_red.size[1] + 15) // 16) * 16))
        pad_red.paste(img_red, (0, 0))
        ov_red = camera.add_overlay(pad_red.tobytes(), format = 'rgba', size=img_red.size)
        ov_red.layer = 3
        overlay_now = "red"
        
        img_orange = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_orange.png')
        pad_orange = Image.new('RGBA', (ov_width, ov_height))
        pad_orange.paste(img_orange, (0, 0), img_orange)
            
        img_yellow = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_yellow.png')
        pad_yellow = Image.new('RGBA', (ov_width, ov_height))
        pad_yellow.paste(img_yellow, (0, 0), img_yellow)
            
        img_green = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_green.png')
        pad_green = Image.new('RGBA', (ov_width, ov_height))
        pad_green.paste(img_green, (0, 0), img_green)
            
        img_cyan = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_cyan.png')
        pad_cyan = Image.new('RGBA', (ov_width, ov_height))
        pad_cyan.paste(img_cyan, (0, 0), img_cyan)
            
        img_blue = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_blue.png')
        pad_blue = Image.new('RGBA', (ov_width, ov_height))
        pad_blue.paste(img_blue, (0, 0), img_blue)
            
        img_violet = Image.open('/home/pi/Desktop/Devastor_camera/overlays/overlay_violet.png')
        pad_violet = Image.new('RGBA', (ov_width, ov_height))
        pad_violet.paste(img_violet, (0, 0), img_violet)
            
        
                
        # By default, the overlay is in layer 0, beneath the
        # preview (which defaults to layer 2). Here we make
        # the new overlay semi-transparent, then move it above
        # the preview

    def __init__(self):
        global worksheet_linux
        global worksheet_usb
        global workbook_linux
        global workbook_usb
        
        # create XLSX worksheets at RasPi and USB-Flash
        workbook_linux = xlsxwriter.Workbook('/home/pi/Desktop/Devastor_camera/points.xlsx')
        worksheet_linux = workbook_linux.add_worksheet()
        workbook_usb = xlsxwriter.Workbook('/media/pi/8FAT/points.xlsx')
        worksheet_usb = workbook_usb.add_worksheet()

        worksheet_linux.write(0, 0, "Snap_No")
        worksheet_linux.write(0, 1, "day,month,year")
        worksheet_linux.write(0, 2, "hour,minute,sec")
        worksheet_linux.write(0, 3, "impulse_value")
        worksheet_linux.write(0, 4, "lattitude")
        worksheet_linux.write(0, 5, "longitude")

        worksheet_usb.write(0, 0, "Snap_No")
        worksheet_usb.write(0, 1, "day,month,year")
        worksheet_usb.write(0, 2, "hour,minute,sec")
        worksheet_usb.write(0, 3, "impulse_value")
        worksheet_usb.write(0, 4, "lattitude")
        worksheet_usb.write(0, 5, "longitude")

        
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        self.window.set_title("Main")
        self.window.connect("destroy", lambda w: gtk.main_quit())

        self.entry = gtk.Entry()
        self.window.show_all()
        
        # Create a Fixed Container
        self.fixed = gtk.Fixed()
        self.fixed.set_name("box")
        self.window.add(self.fixed)
        self.fixed.show()

        #darea = gtk.DrawingArea()
        #darea.size(15, 15)
        #darea.connect("expose-event", self.expose)
        
        #image = gtk.Image()
        #image.set_from_file("rainbow.png")

        #button_capture = gtk.Button("")
        #button_capture.get_child().set_markup("<span font_desc=\"20.0\">SNAP</span>");
        #button_capture.set_size_request(100, 100)
        #button_capture.connect("clicked", self.clicked_capture)
        
        button_exit = gtk.Button("")
        button_exit.get_child().set_markup("<span font_desc=\"20.0\">EXIT</span>");
        button_exit.set_size_request(100, 100)
        button_exit.connect("clicked", self.clicked_exit)
        
        #button_plus = gtk.Button("")
        #button_plus.get_child().set_markup("<span font_desc=\"30.0\">+</span>");
        #button_plus.set_size_request(100, 100)
        #button_plus.connect("clicked", self.clicked_plus)
        
        #button_minus = gtk.Button("")
        #button_minus.get_child().set_markup("<span font_desc=\"30.0\">-</span>");
        #button_minus.set_size_request(100, 100)
        #button_minus.connect("clicked", self.clicked_minus)
        
        impulse_label = gtk.Label("imp")
        lon_label = gtk.Label("lon")
        lat_label = gtk.Label("lat")
        #self.label.set_alignment(20.0, 470)
        
		
        self.fixed.put(button_exit, 700, 380)
        #self.fixed.put(button_capture, 700, 0)
        self.fixed.put(impulse_label, 400, 390)
        self.fixed.put(lon_label, 400, 410)
        self.fixed.put(lat_label, 400, 430)
        #self.fixed.put(button_plus, 0, 0)
        #self.fixed.put(button_minus, 0, 100)
        #self.fixed.put(darea, 0, 190)
        #self.fixed.put(image, 15, 190)
        
        button_exit.show()
        #button_capture.show()
        #button_plus.show()
        #button_minus.show()
        #darea.show()
        #image.show()
        self.window.show()
        lon_label.show()
        lat_label.show()
        impulse_label.show()
        
        global nowTime
        global catched
        global impulse
        global data
        global lat
        global lon
        global overlay_now
        global now_imp
        global camera
        global zoomVal
        zoomVal = 1.0
        
        sleep (1)
	
        camera.framerate = 24
        
        camera.preview_fullscreen=False
        camera.preview_window=(dx, dy, resX, resY)
        camera.resolution = (resX, resY)
        sleep (3)
        camera.start_preview()
        
        self.camera_overlay_init()
        
        nowTime = millis()
        mixer.init()
        mixer.music.load('/home/pi/Desktop/Devastor_camera/alarm.mp3')
        mixer.music.set_volume(0.001)
        mixer.music.play(99999)
        
        oldWheel = 0
        
        while True:
            try:
                data = ser.readline()
            except:
                print("loading")
            if data[0:6] == '$GPGGA':
                msg = pynmea2.parse(data)
                latval = msg.lat
                concatlat = str(latval)[0:10]
                lat = concatlat
                longval = msg.lon
                concatlon = str(longval)[0:10]
                lon = concatlon

            if (millis() - nowTime > 1000):
                camera.annotate_text_size = 40 
                #camera.annotate_foreground = picamera.Color('black')
                #camera.annotate_background = picamera.Color('white')
                #camera.annotate_text = '        In 1 sec: ' + str(impulse) + '                                                                                                                                                                                   ' + str(lat) + ' ' + str(lon)
                #text_gps =  # + " " + str(lat) + " " str(lon)
                
                #impulse_label.set_text(str(impulse))
                impulse_label.set_text(str(mcp.read_adc(0)))
                
                lat_label.set_text(str(lat))
                lon_label.set_text(str(lon))
                #y = 100+300*(impulse/(MAX_UF * 1.0))
                #self.moveWidget(darea, y)

                # CHECK DA SOUND!
                if (impulse < 10): mixer.music.set_volume(0.001)
                elif (impulse < 30): mixer.music.set_volume(0.05)
                elif (impulse < 50): mixer.music.set_volume(0.5)
                elif (impulse >= 50): mixer.music.set_volume(1)
                

                now_imp = impulse
                impulse = 0
                nowTime = millis()

            if (GPIO.input(14) == True & catched == True):
                impulse = impulse + 1
                catched = False
            elif (GPIO.input(14) == False):
                catched = True
            
            potVal = mcp.read_adc(0)
            if (potVal < 140):
                if (zoomVal != 1.0):
                    camera.zoom = (0, 0, 1.0, 1.0)
                    zoomVal = 1.0
            if (potVal > 150 and potVal < 140*2):
                if (zoomVal != 0.9):
                    camera.zoom = (0, 0, 0.9, 0.9)
                    zoomVal = 0.9
            if (potVal > 149*2 and potVal < 149*3):
                if (zoomVal != 0.8):
                    camera.zoom = (0, 0, 0.8, 0.8)
                    zoomVal = 0.8
            if (potVal > 150*3 and potVal < 150*4):
                if (zoomVal != 0.7):
                    camera.zoom = (0, 0, 0.7, 0.7)
                    zoomVal = 0.7
            if (potVal > 151*4 and potVal < 151*5):
                if (zoomVal != 0.6):
                    camera.zoom = (0, 0, 0.6, 0.6)
                    zoomVal = 0.6
            if (potVal > 152*6 and potVal < 152*7):
                if (zoomVal != 0.5):
                    camera.zoom = (0, 0, 0.5, 0.5)
                    zoomVal = 0.5
            if (potVal > 153*7 and potVal < 1024):
                if (zoomVal != 0.4):
                    camera.zoom = (0, 0, 0.4, 0.4)
                    zoomVal = 0.4
            
            
            #oldWheel = mcp.read_adc(0)
            
            while gtk.events_pending():
                gtk.main_iteration()    
        curses.endwin()
	
MainWin = MainClass()
   
