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
    config.c.cfg.common = defaults
    config.save()
conf = config.c.cfg.common

def dimmer(x):
    global conf
    if not conf.dimmer: conf.dimmer = 50
    elif conf.dimmer < 0: conf.dimmer = 1
    elif conf.dimmer > 100: conf.dimmer = 100
    return head.dimcolor(head.findcolor(x), int(conf.dimmer))


def ui_gen():
    global conf
    if conf is None or not conf:
        conf = defaults
        config.save()
    u = ui.UIBuilder("common", "Head configuration")
    u.req("range", "brightness", "Brightness level", low=1, high=255, step=1)
    u.req("range", "dimmer", "Eye brightness adjust", low=1, high=100, step=1)
    u.req("color", "eyel", "Left eye")
    u.req("color", "eyer", "Right eye")
    u.req("color", "antl", "Left antennae")
    u.req("color", "antr", "Right antennae")
    u.req("checkbox", "reset", "Reset colors to defaults")
    u.run("Save settings")
    return u.end()

def handler(params):
    global conf
    if conf.reset:
        del conf.reset
        conf = defaults
        config.save()
    head.brightness(int(conf.brightness))
    head["antl"]=conf["antl"]
    head["antr"]=conf["antr"]
    head["eyel"]=dimmer(conf["eyel"])
    head["eyer"]=dimmer(conf["eyer"])
    head.show()
    return "Head color settings applied."
