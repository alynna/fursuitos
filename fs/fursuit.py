import ui
from addict import Dict
import config
import r
import fsts

# Priority load and render order 0..255 (everything else is loaded last in any order)
if not config.c.mod.fursuit.load: config.c.mod.fursuit.load = 1
if not config.c.mod.fursuit.render: config.c.mod.fursuit.render = 2147483647

conf = config.c.cfg.config

def ui_gen():
    u = ui.UIBuilder("fursuit", "Configure global options")
    options = r.fs.keys()
    u.req("action", "on", "Power on")
    u.req("action", "off", "Power off")
    u.req("multi", "autorun", "Modules to run on startup", options=options)
    u.run("Apply settings")
    return u.end()

def handler(params):
    try:
        params["action"][0]
    except:
        return "Saved configuration."
    if params["action"][0] == "on":
        # Turning a fursuit part on simply calls its autorun method again.
        if config.c.cfg.fursuit.autorun:
            for j in config.c.cfg.fursuit.autorun:
                if not callable(r.fs[j].handler): continue
                try:
                    r.fs[j].handler(None)
                except:
                    r.ERR()
        return "Your fursuit {part} is now ON.".format(part=config.c.part)
    elif params["action"][0] == "off":
        # To turn off a fursuit part, kill its process groups
        for j in [*r.proc]:
            if j.find("_") > -1:
                fsts.stop(j)
        # Then call the off() method for all hardware.
        for j in [*r.hw.drv]:
            if callable(r.hw.drv[j].off):
                r.hw.drv[j].off()
        return "Your fursuit {part} is now OFF.".format(part=config.c.part)
