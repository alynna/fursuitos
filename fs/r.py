# FSOS: Registries.
# Do not import any other modules from here.
# But add this to your file like this:
#  from reg import version, ui, fs, hw, c, gets, sets
# Registries should always be of type "Dict".
from addict import Dict
import sys, traceback
from html import escape
import fsts
from camel import Camel, CamelRegistry
import pprint, config, os
caramel = CamelRegistry()

version=0.5

ui=Dict()
fs=Dict()
hw=Dict()
proc=Dict()
cron=Dict()

def extget(k):
    try:
        with open("/run/shm/"+k) as q:
            return q.read()
    except: return {}

def extset(k,v):
    with open("/run/shm/"+k,"w") as q:
        try: return q.write(v)
        except: raise KeyError("Error writing to file.")

def STOP(mode):
    # Stop all tasks
    fsts.killall()
    # Power down all hardware modules
    for j in [*hw]:
        if callable(hw[j].off):
            hw[j].off()
    # Announce close
    say("[ALL YO YENS YIP YIP YAP] Closing FursuitOS shell.")
    # if restarting, set up shell to restart me
    if mode == "restart":
        os.system("""bash -c "sleep 1; cd /fs; ./fursuitos.py" &""")
    # KYS
    os.system("""bash -c "sleep 0.25; pkill -9 -f 'python3.*fursuitos' &" """)
    sys.exit(0)

def say(x,*args,**kwargs):
    with open("/run/shm/fursuitos.log","a+") as f:
        f.write(escape("{x}\n".format(x=x)))
    print(x,*args,**kwargs)
    
def gets(x):
    """Get from registry with propname as a string"""
    exec("return {x}".format(x=x))

def sets(x,y):
    """Set registry with propname as a string"""
    exec("{x}={y}".format(x=x,y=y))

def regdump():
    x="\n=== Configuration ===\n"
    x+=Camel([caramel]).dump(config.c.to_dict())
    x+="\n=== Fursuit modules ===\n"
    x+=pprint.pformat(fs)
    x+="\n=== User interface ===\n"
    x+=pprint.pformat(ui)
    x+="\n=== Device tree ===\n"
    x+=pprint.pformat(hw)
    x+="\n=== Process scheduler ===\n"
    x+=pprint.pformat(proc)
    x+="\n=== Crontab ===\n"
    x+=pprint.pformat(cron)
    x+="\n=== Network info ===\n"
    x+="Address: {0}\n".format(r.extget("ip"))
    x+="Gateway: {0}\n".format(r.extget("gateway"))
    return x

def ERR():
    if sys.exc_info() is not None:
        say("==================== Your exception, sir. ====================")
        say(str(sys.exc_info()[0])+" : "+str(sys.exc_info()[1])+"\n"+
             traceback.format_exc())
        say("==============================================================")

say("[Yerf] Registries loaded.")
