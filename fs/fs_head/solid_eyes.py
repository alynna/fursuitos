import ui
from addict import Dict
import config
import r
import fsts
import time
import random

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.solid_eyes.render: config.c.mod.solid_eyes.render = 15

head = r.hw.drv.neopx.px
defaults = Dict({ 
    "speed": 64,
    "eyel": "#ff8000",
    "eyer": "#ff8000",
    "mode": "Default",
    })

if not config.c.cfg.solid_eyes or config.c.cfg.solid_eyes == "None":
    config.c.cfg.solid_eyes = defaults
    config.save()

conf = config.c.cfg.solid_eyes
com = config.c.cfg.common

def dimmer(x):
    global com
    if not com.dimmer: com.dimmer = 50
    elif com.dimmer < 0: com.dimmer = 1
    elif com.dimmer > 100: com.dimmer = 100
    return head.dimcolor(x, com.dimmer)

def solid():
    global conf,com
    try:
        while True:
            if conf.mode == "Custom":
                eyel = conf.eyel
                eyer = conf.eyer
            elif conf.mode == "Random":
                eyel = None
                eyer = None
            else:
                eyel = com.eyel
                eyer = com.eyer
            if conf.mode == "Random":
                randl = random.randint(0,16777216)
                randr = random.randint(0,16777216)
            if eyel is not None:
                rl = int(head.findcolor_component(eyel, "r"))
                gl = int(head.findcolor_component(eyel, "g"))
                bl = int(head.findcolor_component(eyel, "b"))
            else:
                rl = int(head.findcolor_component(randl, "r"))
                gl = int(head.findcolor_component(randl, "g"))
                bl = int(head.findcolor_component(randl, "b"))
            if eyer is not None:
                rr = int(head.findcolor_component(eyer, "r"))
                gr = int(head.findcolor_component(eyer, "g"))
                br = int(head.findcolor_component(eyer, "b"))
            else:
                rr = int(head.findcolor_component(randr, "r"))
                gr = int(head.findcolor_component(randr, "g"))
                br = int(head.findcolor_component(randr, "b"))
            head["eyel"]=dimmer(head.findcolor([rl,gl,bl]))
            head["eyer"]=dimmer(head.findcolor([rr,gr,br]))
            head.show()
            time.sleep(conf.time/1000)
    except:
        r.ERR()

def ui_gen():
    u = ui.UIBuilder("solid_eyes", "Eyes solid color")
    u.req("color", "eyel", "Left custom color")
    u.req("color", "eyer", "Right custom color")
    options = [ "Default", "Custom", "Random" ]
    u.req("radio", "mode", "Color set", options=options)
    u.req("number", "time", "Time between changes (ms)", low=0, high=86400000, step=10)
    u.run("Activate solid")
    return u.end()

def handler(params):
    fsts.bgprocess("solid_eyes",solid)
    return "Eyes are now solid.  ti$={ti}".format(ti=conf.time)
