import ui
from addict import Dict
import config
import r
import fsts
import time
import random

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.throb_eyes.render: config.c.mod.throb_eyes.render = 8

head = r.hw.drv.neopx.px

def dimmer(x):
    global com
    if not com.dimmer: com.dimmer = 50
    elif com.dimmer < 0: com.dimmer = 1
    elif com.dimmer > 100: com.dimmer = 100
    return head.dimcolor(x, com.dimmer)

defaults = Dict({ 
    "speed": 64,
    "eyel": "#ff8000",
    "eyer": "#ff8000",
    "mode": "Default",
    })

if not config.c.cfg.throb_eyes or config.c.cfg.throb_eyes == "None":
    config.c.cfg.throb_eyes.update(defaults)
    config.save()

conf = config.c.cfg.throb_eyes
com = config.c.cfg.common

def throb():
    global conf,com
    throb = -255.0
    randl = random.randint(0,16777216)
    randr = random.randint(0,16777216)
    try:
        if conf.mode == "Custom":
            eyel = conf.eyel
            eyer = conf.eyer
        elif conf.mode == "Random":
            eyel = None
            eyer = None
        else:
            eyel = com.eyel
            eyer = com.eyer
        while True:
            # eyes throb section
            if throb > 255.0: throb = -255.0
            throb = throb + 1.0
            if throb == 0.0:
                randl = random.randint(0,16777216)
                randr = random.randint(0,16777216)
            if eyel is not None:
                rl = int(head.findcolor_component(eyel, "r") * (abs(throb)/256.0))
                gl = int(head.findcolor_component(eyel, "g") * (abs(throb)/256.0))
                bl = int(head.findcolor_component(eyel, "b") * (abs(throb)/256.0))
            else:
                rl = int(head.findcolor_component(randl, "r") * (abs(throb)/256.0))
                gl = int(head.findcolor_component(randl, "g") * (abs(throb)/256.0))
                bl = int(head.findcolor_component(randl, "b") * (abs(throb)/256.0))
            if eyer is not None:
                rr = int(head.findcolor_component(eyer, "r") * (abs(throb)/256.0))
                gr = int(head.findcolor_component(eyer, "g") * (abs(throb)/256.0))
                br = int(head.findcolor_component(eyer, "b") * (abs(throb)/256.0))
            else:
                rr = int(head.findcolor_component(randr, "r") * (abs(throb)/256.0))
                gr = int(head.findcolor_component(randr, "g") * (abs(throb)/256.0))
                br = int(head.findcolor_component(randr, "b") * (abs(throb)/256.0))
            head["eyel"]=dimmer(head.findcolor([rl,gl,bl]))
            head["eyer"]=dimmer(head.findcolor([rr,gr,br]))
            head.show()
            time.sleep(1*(1/(conf.speed if conf.speed >0 else 1)))
    except:
        r.ERR()

def ui_gen():
    u = ui.UIBuilder("throb_eyes", "Eyes throb dim to bright")
    u.req("color", "eyel", "Left custom color")
    u.req("color", "eyer", "Right custom color")
    options = [ "Default", "Custom", "Random" ]
    u.req("radio", "mode", "Throb moode", options=options)
    u.req("range", "speed", "Throb speed", low=1, high=255, step=1)
    u.run("[Eyes] Activate throbbing")
    return u.end()

def handler(params):
    fsts.bgprocess("throb_eyes",throb)
    return "Eyes are now throbbing."

