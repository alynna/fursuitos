#!/usr/bin/python3
with open("/run/shm/fursuitos.log","w+") as f: pass
from http.server import BaseHTTPRequestHandler, HTTPServer
from addict import Dict
from collections import OrderedDict
import pprint
import os,sys,importlib,time
import fsts as ts
import ui
from config import c
import r

r.say("FursuitOS v{0} (C) 2018 Alynna Trypnotk, GPL3".format(r.version))

r.say(pprint.pformat(c))
# Start up the hardware handlers.  Expected to be common between fursuits.
# Config file specifies what is handled
for hwtype in c.hw:
    for hwunit in c.hw[hwtype]:
        try:
            r.hw[hwtype][hwunit].driver = importlib.import_module("hw.{0}".format(c.hw[hwtype][hwunit].interface))
            r.hw[hwtype][hwunit].unit = c.hw[hwtype][hwunit].index
            r.hw.drv[c.hw[hwtype][hwunit].interface] = importlib.import_module("hw.{0}".format(c.hw[hwtype][hwunit].interface))
        except Exception as e:
            r.ERR()
            r.say("[HW] Failed to load {0} due to error {1}.  Skipping module.".format(j[0:-3], e))

r.say("\nDevice tree: \n"+pprint.pformat(r.hw))

# Search for mods and sort them by loading order.
known_mods = c.mod
found_mods = []

# Look for any module that starts with "common" and load it first.
try:
    found_mods += [x[0:-3] for x in os.listdir("./fs/") if x.startswith("common") and x.endswith(".py")]
    found_mods += [x[0:-3] for x in os.listdir("./fs_{0}/".format(c.part)) if x.startswith("common") and x.endswith(".py")]
except:
    pass
if found_mods:
    tmp = {}
    for x in found_mods:
        if not c.mod[x].load == {}:
            tmp[x] = c.mod[x].load
        else:
            tmp[x] = (2 ** 24)
    l = (OrderedDict(sorted(tmp.items(), key=lambda x: x[1]))).keys()
    del tmp
if l:
    for j in l:
        try:
            try:
                r.fs[j] = importlib.import_module("fs_{0}.{1}".format(c.part,j))
            except:
                r.fs[j] = importlib.import_module("fs.{0}".format(j))
        except Exception as e:
            r.ERR()
            r.say("[YIP] Failed to load {0} due to error {1}.  Skipping module.".format(j[0:-3],e))

# Now load all mods.
try:
    found_mods += [x[0:-3] for x in os.listdir("./fs/") if x.endswith(".py")]
    found_mods += [x[0:-3] for x in os.listdir("./fs_{0}/".format(c.part)) if x.endswith(".py")]
except:
    pass
if found_mods:
    tmp = {}
    for x in found_mods:
        if not c.mod[x].load == {}:
            tmp[x] = c.mod[x].load
        else:
            tmp[x] = (2 ** 24)
    l = (OrderedDict(sorted(tmp.items(), key=lambda x: x[1]))).keys()
    del tmp
if l:
    for j in l:
        try:
            try:
                r.fs[j] = importlib.import_module("fs_{0}.{1}".format(c.part,j))
            except:
                r.fs[j] = importlib.import_module("fs.{0}".format(j))
        except Exception as e:
            r.ERR()
            r.say("[YIP] Failed to load {0} due to error {1}.  Skipping module.".format(j[0:-3],e))

r.say("\nModule tree: \n"+pprint.pformat(r.fs))

# Quietly render the UI so I can learn their datatypes
for j in [*r.fs]:
    try:
        r.fs[j].ui_gen()
    except: pass

# Start the configured autorun programs
if c.cfg.fursuit.autorun:
    for j in c.cfg.fursuit.autorun:
        if not callable(r.fs[j].handler): continue
        try:
            r.fs[j].handler(None)
        except:
            r.ERR()
        
# Finally start up the user interface.  This runs until terminated.
server_address = (c.ui.bind, c.ui.port)
httpd = HTTPServer(server_address, ui.FursuitUI)
r.say("\nProcesses:")
os.system("pkill -9 -f /fs/hw/rpi_ws281x/test")
ts.bgthread("httpd", httpd.serve_forever)
ts.ps()
r.say("FursuitOS v{0} (C) 2018 Alynna Trypnotk, GPL3".format(r.version))
r.say('[UI] Started')
try:
    while True: time.sleep(1)
except KeyboardInterrupt as e:
    ts.killall()
    r.say("[ALL YO YENS YIP YIP YAP] Closing FursuitOS shell.")
    sys.exit(0)
except Exception as e:
    r.ERR()
    ts.killall()
    r.say("[YERF] Foxy died..")
    sys.exit(0)

