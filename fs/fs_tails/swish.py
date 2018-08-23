import ui
from addict import Dict
import config
import r
import fsts
import time

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.swish.load: config.c.mod.swish.load = <priority>
if not config.c.mod.swish.render: config.c.mod.swish.render = 31

tails = r.hw.drv.neopx.px
defaults = Dict({
    "speed": 64,
    "delta": 3,
    "color": "#ddddff",
     "mode": "Tail color"
})

cnt = 0

if not config.c.cfg.swish or config.c.cfg.swish == "None":
    config.c.cfg.swish = defaults
    config.save()

conf = config.c.cfg.swish
com = config.c.cfg.common

tnum = [0 for i in range(tails.numPixels())]
for j in [*r.hw.led]:
    tnum[config.c.hw.led[j].index] = tails.findcolor(com[j])
r.say(tnum)

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


def swishgen(x, pix):
    global cnt
    if x == "custom":
        return tails.findcolor(conf.color)
    elif x == "rainbow":
        cnt+=1
        if cnt > 255: cnt = 0
        return wheel(cnt)
    elif x == "default":
        return tnum[pix]
    
def swish(x):
    pos = 0
    dr = 1
    while True:
        tails.fill(0)
        # What's your favorite color tell us please!
        tails.setPixelColor(pos, swishgen(x, pos))
        if conf.delta > 0:
            for j in range(1,conf.delta):
                if (pos - j) >= 0:
                    tails.setPixelColor(pos - j, tails.dimcolor(swishgen(x, pos - j), (1.0 / (j+1))*100))
                if (pos + j) < tails.numPixels():
                    tails.setPixelColor(pos + j, tails.dimcolor(swishgen(x, pos + j), (1.0 / (j+1))*100))
        tails.show()
        if pos <= 0: dr = 1
        elif pos >= tails.numPixels()-1: dr = -1
        pos+=(dr*1)
        time.sleep(2*(101-conf.speed)/100)

def defSwish():
    swish("default")
def custSwish():
    swish("custom")
def rainbowSwish():
    swish("rainbow")

def ui_gen():
    u = ui.UIBuilder("swish", "Tail swish")
    u.run("Save changes")
    u.req("range", "speed", "Speed of animation", low=1, high=100, step=1)
    u.req("range", "delta", "Light occupation delta", low=0, high=tails.numPixels(), step=1)
    u.req("color", "color", "Light custom color")
    u.req("action", "defcolor", "Swish by tail color")
    u.req("action", "custcolor", "Swish custom color")
    u.req("action", "rainbow", "Rainbow swish")
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
    if x == "defcolor":
        fsts.bgprocess("defswish_tails",defSwish)
    elif x == "custcolor":
        fsts.bgprocess("custswish_tails",custSwish)
    elif x == "rainbow":
        fsts.bgprocess("rbswish_tails",rainbowSwish)
    else:
        return ""
    return "{0} program running at speed {1}".format(x,conf.speed)


