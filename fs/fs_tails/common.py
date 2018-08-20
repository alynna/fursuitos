import ui
from addict import Dict
import config
import r

# Priority load and render order 0..255 (everything else is loaded last in any order)
if not config.c.mod.common.load: config.c.mod.common.load = 0
if not config.c.mod.common.render: config.c.mod.common.render = 0

tails = r.hw.drv.neopx.px

defaults = Dict({
    "r": "#ff0000",
    "o": "#ff8000",
    "g": "#00ff00",
    "b": "#0000ff",
    "i": "#00ffff",
    "v": "#ff00ff",
    "brightness": 255
    })

if not config.c.cfg.common:
    config.c.cfg.common = defaults
    config.save()
conf = config.c.cfg.common

def ui_gen():
    global conf
    if conf is None or not conf:
        conf = defaults
        config.save()
    u = ui.UIBuilder("common", "Tails common configuration")
    u.req("range", "brightness", "Brightness level", low=0, high=255, step=1)
    u.req("color", "r", "Red tail")
    u.req("color", "o", "Orange tail")
    u.req("color", "g", "Green tail")
    u.req("color", "b", "Blue tail")
    u.req("color", "i", "Indigo tail")
    u.req("color", "v", "Violet tail")
    u.req("checkbox", "reset", "Reset colors to defaults")
    u.run("Save settings")
    return u.end()

def handler(params):
    global conf
    if conf.reset:
        del conf.reset
        conf = defaults
        config.save()
    tails["r"]=conf["r"]
    tails["o"]=conf["o"]
    tails["g"]=conf["g"]
    tails["b"]=conf["b"]
    tails["i"]=conf["i"]
    tails["v"]=conf["v"]
    tails.brightness(int(conf.brightness))
    tails.show()
    return "Tail color settings applied."
