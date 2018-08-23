import ui
from addict import Dict
import config
import r
import fsts
import time
import random

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.throb_antennae.render: config.c.mod.throb_antennae.render = 8

head = r.hw.drv.neopx.px
defaults = Dict({ 
    "speed": 64,
    "antl": "#ff8000",
    "antr": "#ff8000",
    "mode": "default",
    })

if not config.c.cfg.throb_antennae or config.c.cfg.throb_antennae == "None":
    config.c.cfg.throb_antennae.update(defaults)
    config.save()

conf = config.c.cfg.throb_antennae
com = config.c.cfg.common

def throb():
    global conf,com
    throb = -255.0
    randl = random.randint(0,16777216)
    randr = random.randint(0,16777216)
    try:
        if conf.mode == "Custom":
            antl = conf.antl
            antr = conf.antr
        elif conf.mode == "Random":
            antl = None
            antr = None
        else:
            antl = com.antl
            antr = com.antr
        while True:
            # Antennae throb section
            if throb > 255.0: throb = -255.0
            throb = throb + 1.0
            if throb == 0.0:
                randl = random.randint(0,16777216)
                randr = random.randint(0,16777216)
            if antl is not None:
                rl = int(head.findcolor_component(antl, "r") * (abs(throb)/256.0))
                gl = int(head.findcolor_component(antl, "g") * (abs(throb)/256.0))
                bl = int(head.findcolor_component(antl, "b") * (abs(throb)/256.0))
            else:
                rl = int(head.findcolor_component(randl, "r") * (abs(throb)/256.0))
                gl = int(head.findcolor_component(randl, "g") * (abs(throb)/256.0))
                bl = int(head.findcolor_component(randl, "b") * (abs(throb)/256.0))
            if antr is not None:
                rr = int(head.findcolor_component(antr, "r") * (abs(throb)/256.0))
                gr = int(head.findcolor_component(antr, "g") * (abs(throb)/256.0))
                br = int(head.findcolor_component(antr, "b") * (abs(throb)/256.0))
            else:
                rr = int(head.findcolor_component(randr, "r") * (abs(throb)/256.0))
                gr = int(head.findcolor_component(randr, "g") * (abs(throb)/256.0))
                br = int(head.findcolor_component(randr, "b") * (abs(throb)/256.0))
            head["antl"]=head.findcolor([rl,gl,bl])
            head["antr"]=head.findcolor([rr,gr,br])
            head.show()
            time.sleep(1*(1/(conf.speed if conf.speed >0 else 1)))
    except:
        r.ERR()

def ui_gen():
    u = ui.UIBuilder("throb_antennae", "Antennae throb dim to bright")
    u.req("color", "antl", "Left custom color")
    u.req("color", "antr", "Right custom color")
    options = [ "Default", "Custom", "Random" ]
    u.req("radio", "mode", "Throb moode", options=options)
    u.req("range", "speed", "Throb speed", low=1, high=255, step=1)
    u.run("[Antennae] Activate throbbing")
    return u.end()

def handler(params):
    fsts.bgprocess("throb_antennae",throb)
    return "Antennae are now throbbing."

