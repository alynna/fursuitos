import ui
from addict import Dict
import config
import r
import fsts
import time

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.rainbow.render: 
    config.c.mod.rainbow.render = 64
    config.save()

tails = r.hw.drv.neopx.px
defaults = Dict({ "speed": 64 })

if not config.c.cfg.rainbow or config.c.cfg.rainbow == "None":
    config.c.cfg.rainbow.update(defaults)
    config.save()

conf = config.c.cfg.rainbow
com = config.c.cfg.common

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return r.hw.drv.neopx.Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return r.hw.drv.neopx.Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return r.hw.drv.neopx.Color(0, pos * 3, 255 - pos * 3)

def colorWipe(color):
    """Wipe color across display a pixel at a time."""
    for i in range(tails.numPixels()):
        tails.setPixelColor(i, color)
        tails.show()
        time.sleep(1.0/(conf.speed*4))

def rainbow():
    """Draw rainbow that fades across all pixels at once."""
    j=0
    while True:
        j+=1
        for i in range(tails.numPixels()):
            tails.setPixelColor(i, wheel((i+j) & 255))
        tails.show()
        if r.proc["rainbow_tails"].die: return
        time.sleep(4*(1/conf.speed))

def rainbowCycle():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    j=0
    while True:
        j=(j+1)
        for i in range(tails.numPixels()):
            tails.setPixelColor(i, wheel((int(i * 256 / tails.numPixels()) + j) & 255))
        tails.show()
        if r.proc["cycle_tails"].die: return
        time.sleep(4*(1/conf.speed))

def rainbowChase():
    """Rainbow movie theater light style chaser animation."""
    j=0
    while True:
        j=(j+1) % 256
        for j in range(256):
            for q in range(3):
                for i in range(0, tails.numPixels(), 3):
                    tails.setPixelColor(i+q, wheel((i+j) % 255))
                tails.show()
                if r.proc["chase_tails"].die: return
                time.sleep(4*(1/conf.speed))
                for i in range(0, tails.numPixels(), 3):
                    tails.setPixelColor(i+q, 0)

def ui_gen():
    u = ui.UIBuilder("rainbow", "Tail rainbows")
    u.req("range", "speed", "Speed of animation", low=1, high=255, step=1)
    u.run("Save changes to speed")
    u.req("action", "cycle", "Do cycling rainbow anim")
    u.req("action", "rainbow", "Do rainbow anim")
    u.req("action", "chase", "Do chasing rainbow anim")
    return u.end()

def handler(params):
    try:
        x = params["action"][0]
        conf.last_action = x
        config.save()
    except:
        if not conf.last_action == {}:
            x = conf.last_action
    tails.brightness(com.brightness)
    if x == "cycle":
        fsts.bgprocess("cycle_tails",rainbowCycle)
    elif x == "rainbow":
        fsts.bgprocess("rainbow_tails",rainbow)
    elif x == "chase":
        fsts.bgprocess("chase_tails",rainbowChase)
    else:
        return ""
    return "{0} program running at speed {1}".format(x,conf.speed)


