import ui
from addict import Dict
import config
import r
import fsts
import time
import random

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.solid_antennae.render: config.c.mod.solid_antennae.render = 15

head = r.hw.drv.neopx.px
defaults = Dict({ 
    "speed": 64,
    "antl": "#ff8000",
    "antr": "#ff8000",
    "mode": "default",
    })

if not config.c.cfg.solid_antennae or config.c.cfg.solid_antennae == "None":
    config.c.cfg.solid_antennae = defaults
    config.save()

conf = config.c.cfg.solid_antennae
com = config.c.cfg.common

def solid():
    global conf,com
    try:
        if conf.mode == "Custom":
            antl = conf.antl
            antr = conf.antl
        elif conf.mode == "Random":
            antl = None
            antr = None
        else:
            antl = com.antl
            antr = com.antr
        while True:
            if conf.mode == "Random":
                randl = random.randint(0,16777216)
                randr = random.randint(0,16777216)
            if antl is not None:
                rl = int(head.findcolor_component(antl, "r"))
                gl = int(head.findcolor_component(antl, "g"))
                bl = int(head.findcolor_component(antl, "b"))
            else:
                rl = int(head.findcolor_component(randl, "r"))
                gl = int(head.findcolor_component(randl, "g"))
                bl = int(head.findcolor_component(randl, "b"))
            if antr is not None:
                rr = int(head.findcolor_component(antr, "r"))
                gr = int(head.findcolor_component(antr, "g"))
                br = int(head.findcolor_component(antr, "b"))
            else:
                rr = int(head.findcolor_component(randr, "r"))
                gr = int(head.findcolor_component(randr, "g"))
                br = int(head.findcolor_component(randr, "b"))
            head["antl"]=head.findcolor([rl,gl,bl])
            head["antr"]=head.findcolor([rr,gr,br])
            head.show()
            time.sleep(conf.time/1000)
    except:
        r.ERR()

def ui_gen():
    u = ui.UIBuilder("solid_antennae", "Antennae solid color")
    u.req("color", "antl", "Left custom color")
    u.req("color", "antr", "Right custom color")
    options = [ "Default", "Custom", "Random" ]
    u.req("radio", "mode", "Color set", options=options)
    u.req("number", "time", "Time between changes (ms)", low=0, high=86400000, step=10)
    u.run("Activate solid")
    return u.end()

def handler(params):
    fsts.bgprocess("solid_antennae",solid)
    return "Antennae are now solid.  ti$={ti}".format(ti=conf.time)
