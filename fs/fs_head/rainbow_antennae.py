import ui
from addict import Dict
import config
import r
import fsts
import time

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.rainbow_antennae.render: config.c.mod.rainbow_antennae.render = 63

head = r.hw.drv.neopx.px
defaults = Dict({
    "speed": 64,
    "last_action": "rainbow",
    })

if not config.c.cfg.rainbow_antennae or config.c.cfg.rainbow_antennae == "None":
    config.c.cfg.rainbow_antennae = defaults
    config.save()

conf = config.c.cfg.rainbow_antennae
com = config.c.cfg.common
antennae = [x for x in config.c.hw.led.keys() if x.startswith("ant")]

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

def rainbow():
    """Draw rainbow that fades across all pixels at once."""
    j=0
    while True:
        j+=1
        for i in antennae:
            head[i]=wheel(int((config.c.hw.led[i].index % len(antennae))+j) & 255)
        head.show()
        if r.proc["rainbow_antennae"].die: return
        time.sleep(4*(1/conf.speed))

def rainbowCycle():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    j=0
    while True:
        j=(j+1)
        for i in antennae:
            head[i]=wheel(int((int(config.c.hw.led[i].index % len(antennae)) * 256 / len(antennae)) + j) & 255)
        head.show()
        if r.proc["cycle"].die: return
        time.sleep(4*(1/conf.speed))

def ui_gen():
    u = ui.UIBuilder("rainbow_antennae", "Antennae rainbows")
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
    if x == "cycle":
        fsts.bgprocess("cycle_antennae",rainbowCycle)
    elif x == "rainbow":
        fsts.bgprocess("rainbow_antennae",rainbow)
    else:
        return ""
    return "{0} program running at speed {1}".format(x,conf.speed)


