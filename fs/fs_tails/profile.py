import ui
from addict import Dict
import config
from config import c
import r
import fsts

# Priority load and render order 0..255 (everything else is loaded last)
#if not config.c.mod.rainbow.load: config.c.mod.rainbow.load = <priority>
if not config.c.mod.rainbow.render: config.c.mod.rainbow.render = 2

tails = r.hw.drv.neopx.px

defaults = Dict({
    "default": "Current settings"
    })

if not config.c.cfg.profile:
    config.c.cfg.profile = defaults
    config.save()
conf = c.cfg.profile
    
com = c.cfg.common

def ui_gen():
    global conf,com
    u = ui.UIBuilder("profile", "Tail color configs")
    options = [
        "Current settings",
        "By tailtip color",
        "All white",
        "Half luminosity",
        "Off"
        ]
    u.req("select", "default", "Tailtip default quickset", options=options)
    u.run("Apply quick color set")
    return u.end()

def handler(params):
    global conf,com
    if conf.default == "By tailtip color":
        tails["r"]="ff0000"
        tails["o"]="ff8000"
        tails["g"]="00ff00"
        tails["b"]="0000ff"
        tails["i"]="00ffff"
        tails["v"]="ff00ff"
    elif conf.default == "All white":
        tails["r"]="ffffff"
        tails["o"]="ffffff"
        tails["g"]="ffffff"
        tails["b"]="ffffff"
        tails["i"]="ffffff"
        tails["v"]="ffffff"
    elif conf.default == "Half luminosity":
        tails["r"]="7f0000"
        tails["o"]="7f3f00"
        tails["g"]="007f00"
        tails["b"]="00007f"
        tails["i"]="007f7f"
        tails["v"]="00007f"
    elif conf.default == "Current settings":
        tails["r"]=com["r"]
        tails["o"]=com["o"]
        tails["g"]=com["g"]
        tails["b"]=com["b"]
        tails["i"]=com["i"]
        tails["v"]=com["v"]
    else:
        tails.brightness(0)
    fsts.stopgroup("tails")
    tails.show()
    tails.brightness(com.brightness)
    return "Tail color settings applied."
