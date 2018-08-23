import ui
from addict import Dict
import config
import r

# Priority load and render order 0..255 (everything else is loaded last in any order)
if not config.c.mod.common.load: config.c.mod.common.load = 0
if not config.c.mod.common.render: config.c.mod.common.render = 0

head = r.hw.drv.neopx.px

defaults = Dict({
    "antl": "#ff8000",
    "antr": "#ff8000",
    "eyel": "#004080",
    "eyer": "#004080",
    "brightness": 255,
    "dimmer": 50
    })

if not config.c.cfg.common:
    config.c.cfg.common.update(defaults)
    config.save()

def dimmer(x):
    if not config.c.cfg.common.dimmer: config.c.cfg.common.dimmer = 50
    elif config.c.cfg.common.dimmer < 0: config.c.cfg.common.dimmer = 1
    elif config.c.cfg.common.dimmer > 100: config.c.cfg.common.dimmer = 100
    return head.dimcolor(head.findcolor(x), int(config.c.cfg.common.dimmer))


def ui_gen():
    u = ui.UIBuilder("common", "Head configuration")
    u.req("range", "brightness", "Brightness level", low=1, high=255, step=1)
    u.req("range", "dimmer", "Eye brightness adjust", low=1, high=100, step=1)
    u.req("color", "eyel", "Left eye")
    u.req("color", "eyer", "Right eye")
    u.req("color", "antl", "Left antennae")
    u.req("color", "antr", "Right antennae")
    u.req("action", "reset", "Reset colors to defaults")
    u.run("[Head] Save settings")
    return u.end()

def handler(params):
    action = ""
    try:
        action = params["action"][0]
    except: pass
    if action == "reset":
        config.c.cfg.common.update(defaults)
        config.save()
    head.brightness(int(config.c.cfg.common.brightness))
    head["antl"]=config.c.cfg.common["antl"]
    head["antr"]=config.c.cfg.common["antr"]
    head["eyel"]=dimmer(config.c.cfg.common["eyel"])
    head["eyer"]=dimmer(config.c.cfg.common["eyer"])
    head.show()
    return "Head color settings applied."
