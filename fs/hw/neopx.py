#!/usr/bin/env python3
# fs/hw/neopx.py - Neopixel driver for fursuitOS
# Note: this driver is thread friendly

import time, math, random
from neopixel import *
import r
import config
from config import c
import pprint
import ctypes
import mmap
import pickle

# Shared memory for the pixel gods
shm = mmap.mmap(-1,4)
shm.seek(0)

class LED(Adafruit_NeoPixel):
    def __init__(self):
        self.LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        self.LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
        self.LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        self.LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        self.LED_COUNT      = 0
        for j in [*c.hw.led]:
            if c.hw.led[j].interface == "neopx":
                self.LED_COUNT+=1
                setattr(self,j,c.hw.led[j].index)
        super().__init__(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.leds = [0 for i in range(self.LED_COUNT)]
        self.shm = shm
        self.shm.resize(self.LED_COUNT*4)
        r.say("[neopx] shared memory size is {x}".format(x=self.LED_COUNT*4))
        try:
            self.read()
        except:
            pass
        self.begin()
        for j in range(self.numPixels()):
            if self.leds[j] == 0:
                self.leds[j] = super().getPixelColor(j)
        self.write()
    def write(self):
        self.shm.seek(0)
        for j in range(self.numPixels()):
            self.shm.write(self.leds[j].to_bytes(4,"big"))
    def read(self):
        self.shm.seek(0)
        for j in range(self.numPixels()):
            self.leds[j] = int.from_bytes(self.shm.read(4),byteorder="big")
    def dim_component(self, x, pct=50):
        if x * (pct/100) < 1:
            return 1
        elif x * (pct/100) > 255:
            return 255
        else:
            return x * (pct/100)
    def dimcolor(self, x, pct=50):
        return int.from_bytes([int(x.to_bytes(4, "big")[1] * (pct/100.0)), int(x.to_bytes(4, "big")[2] * (pct/100)), int(x.to_bytes(4, "big")[3] * (pct/100))], "big")
    def findled(self,x):
        if isinstance(x, int):
            return x
        elif isinstance(x, str):
            return getattr(self, x)
        else:
            return self[x]
    def findcolor_component(self, c, comp):
        x = self.findcolor(c)
        if comp == "r": return x.to_bytes(4, "big")[1]
        elif comp == "g": return x.to_bytes(4, "big")[2]
        elif comp == "b": return x.to_bytes(4, "big")[3]
        else: return x.to_bytes(4, "big")[0]
    def findcolor(self,x):
        if isinstance(x, int):
            return x
        elif isinstance(x, str):
            if x[0]=="#":
                x=x[1:-1]
            return Color(int(x[0:2],base=16),int(x[2:4],base=16),int(x[4:6],base=16))
        elif isinstance(x, list):
            return Color(x[0],x[1],x[2])
        elif isinstance(x, dict):
            return Color(x["r"],x["g"],x["b"])
        else:
            r.ERR()
            return 0
    def setPixelColor(self, x, c):
        self.read()
        self.leds[x] = c
        self.write()
        super().setPixelColor(x,c)
    def show(self):
        self.read()
        for j in range(self.numPixels()):
            super().setPixelColor(j,self.leds[j])
        super().show()
    def __getitem__(self, x):
        try:
            self.getPixelColor(self.findled(x))
        except:
            r.ERR()
            return -1
    def __setitem__(self, x, c):
        try:
            self.setPixelColor(self.findled(x), self.findcolor(c))
        except:
            r.ERR()
    def __len__(self):
        return self.numPixels()
    def __default__(self):
        return self.getPixels()
    def fill(self, color, show=False):
        """Wipe color across display a pixel at a time."""
        for i in range(self.numPixels()):
            self.setPixelColor(i, color)
            if show: self.show()
    def off(self):
        for i in range(self.numPixels()):
            self.setPixelColor(i, Color(0,0,0))
        self.show()
        time.sleep(0.001)
    def brightness(self,b):
        self.setBrightness(b)
        self.show()

def off():
    px.off()

# Main screen turn on
px = LED()
px.brightness(255)

