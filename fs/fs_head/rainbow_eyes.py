import ui
from addict import Dict
import config
import r
import fsts
import time

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.rainbow_eyes.render: config.c.mod.rainbow_eyes.render = 63

head = r.hw.drv.neopx.px
defaults = Dict({
    "speed": 64,
    "last_action": "rainbow",
    })

if not config.c.cfg.rainbow_eyes or config.c.cfg.rainbow_eyes == "None":
    config.c.cfg.rainbow_eyes = defaults
    config.save()

conf = config.c.cfg.rainbow_eyes
com = config.c.cfg.common
eyes = [x for x in config.c.hw.led.keys() if x.startswith("eye")]

def dimmer(x):
    global com
    if not com.dimmer: com.dimmer = 50
    elif com.dimmer < 0: com.dimmer = 1
    elif com.dimmer > 100: com.dimmer = 100
    return head.dimcolor(x, com.dimmer)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return r.hw.drv.neopx.Color(pos*3, 255-pos*3, 0)
    elif pos < 170:
        pos -= 85
        return r.hw.drv.neopx.Color(255-pos*3, 0, pos*3)
    else:
        pos -= 170
        return r.hw.drv.neopx.Color(0, pos*3, 255 - pos * 3)

def rainbow():
    """Draw rainbow that fades across all pixels at once."""
    j=0
    while True:
        j+=1
        for i in eyes:
            head[i]=dimmer(wheel(int((config.c.hw.led[i].index % len(eyes))+j) & 255))
        head.show()
        if r.proc["rainbow_eyes"].die: return
        time.sleep(4*(1/conf.speed))

def rainbowCycle():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    j=0
    while True:
        j+=1
        for i in eyes:
            head[i]=dimmer(wheel(int(((int(config.c.hw.led[i].index) % len(eyes)) * 256 / len(eyes)) + j) & 255))
        head.show()
        if r.proc["cycle_eyes"].die: return
        time.sleep(4*(1/conf.speed))

def ui_gen():
    u = ui.UIBuilder("rainbow_eyes", "Eye rainbows")
    u.req("range", "speed", "Speed of animation", low=1, high=255, step=1)
    u.run("Save changes to speed")
    u.req("action", "cycle", "Do cycling rainbow anim")
    u.req("action", "rainbow", "Do rainbow anim")
    return u.end()

def handler(params):
    try:
        x = params["action"][0]
        conf.last_action = x
        config.save()
    except:
        if not conf.last_action == {}:
            x = conf.last_action
        else:
            x = "rainbow"
    if not com.dimmer: 
        dimmer = 50
        config.save()
    if x == "cycle":
        fsts.bgprocess("cycle_eyes",rainbowCycle)
    elif x == "rainbow":
        fsts.bgprocess("rainbow_eyes",rainbow)
    else:
        return ""
    return "{0} program running at speed {1}".format(x,conf.speed)


