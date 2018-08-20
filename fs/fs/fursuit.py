import ui
from addict import Dict
import config
import r

# Priority load and render order 0..255 (everything else is loaded last in any order)
if not config.c.mod.fursuit.load: config.c.mod.fursuit.load = 1
if not config.c.mod.fursuit.render: config.c.mod.fursuit.render = 2147483647

conf = config.c.cfg.config

def ui_gen():
    u = ui.UIBuilder("fursuit", "Configure global options")
    options = r.fs.keys()
    u.req("multi", "autorun", "Modules to run on startup", options=options)
    u.run("Apply settings")
    return u.end()

def handler(params):
    return "Saved configuration."
