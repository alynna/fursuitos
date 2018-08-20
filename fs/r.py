# FSOS: Registries.
# Do not import any other modules from here.
# But add this to your file like this:
#  from reg import version, ui, fs, hw, c, gets, sets
# Registries should always be of type "Dict".
from addict import Dict
import sys, traceback
from html import escape
from camel import Camel, CamelRegistry
import pprint, config
caramel = CamelRegistry()

version=0.4

ui=Dict()
fs=Dict()
hw=Dict()
proc=Dict()
cron=Dict()

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
    return x

def ERR():
    if sys.exc_info() is not None:
        say("==================== Your exception, sir. ====================")
        say(str(sys.exc_info()[0])+" : "+str(sys.exc_info()[1])+"\n"+
             traceback.format_exc())
        say("==============================================================")


say("Registries loaded.")
