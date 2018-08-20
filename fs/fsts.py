# fs/fsts.py - FursuitOS task scheduler
import os, sys, signal
from multiprocessing import Process
from threading import Thread
from addict import Dict
import time, math
from config import c
from html import escape
import r
import pprint

exitFlag = 0

def no(x,y):
    pass

def bgprocess(name, func, *args, **kwargs):
    """Starts a background process.  Can be separated from our process.
       Give all information it will need through its args and kwargs
    """
    if "_" in name:
        name, group = name ,name.split("_")[1]
    else:
        name, group = name, name
    # Only one process of a process group is permitted to run.
    # Use process groups for hardware modules so that only one
    # process in this group will be accessing a certain set of
    # hardware at a time.
    for j in [*r.proc]:
        try:
            r.proc[j]
            if r.proc[j].group == group: stop(j)
        except: pass
    process = Process(name=name, target=func, args=args, kwargs=kwargs)
    process.daemon = True
    r.proc[name].func = func
    r.proc[name].process = process
    r.proc[name].group = group
    r.proc[name].args = args
    r.proc[name].kwargs = kwargs
    r.proc[name].type = "process"
    r.proc[name].die = False
    process.start()
    ps()
    return r.proc[name]

def bgthread(name, func, *args, **kwargs):
    """Starts a background thread."""
    if "_" in name:
        name, group = name, name.split("_")[1]
    else:
        name, group = name, name
    for j in [*r.proc]:
        if r.proc[j].group == group: stop(r.proc[j].name)
    process = Thread(name=name, target=func, args=args, kwargs=kwargs)
    process.daemon = True
    r.proc[name].func = func
    r.proc[name].process = process
    r.proc[name].group = group
    r.proc[name].args = args
    r.proc[name].kwargs = kwargs
    r.proc[name].type = "thread"
    r.proc[name].die = False
    process.start()
    ps()
    return r.proc[name]

def stopgroup(group):
    for j in [*r.proc]:
        if r.proc[j].group == group: stop(j)
    
def stop(name):
    """Stop a background process by name.  Also the proper way for a bg process to end."""
    if r.proc[name].type == "process":
        r.proc[name].process.terminate()
        time.sleep(0.09)
    else:
        if callable(r.proc[name].process.is_alive()):
            r.proc[name].die = True
            while r.proc[name].process.is_alive():
                r.proc[name].process.join(0.01)
                time.sleep(0.09)
    del r.proc[name]
    ps()
        
def killall():
    for j in [*r.proc]:
        stop(j)
    
def crond():
    """Runs scheduled processes with a resolution of a second.
    NOTE that your process is only guaranteed to run within that second, not at the beginning."""
    tick = 0   # Immediate check when cron starts for jobs.
    while True:
        # Snooze till the next second.
        while tick >= math.floor(time.time()):
            time.sleep(0.5)
            if r.proc["VixenCron"].die: return
        tick = math.floor(time.time())
        # Schedule any due cron jobs.
        for j in [*r.cron]:
            if not (tick % r.cron[j].interval):
                if r.cron[j].type == "process":
                    bgprocess(j, r.cron[j].func, r.cron[j].args, r.cron[j].kwargs)
                else:
                    bgthread(j, r.cron[j].func, r.cron[j].args, r.cron[j].kwargs)
        # Clean up dead processes.
        for j in [*r.proc]:
            if not r.proc[j].process.is_alive():
                del r.proc[j]
        # And repeat.
            
def cronjob(name, func, interval, thread=True, *args, **kwargs):
    """Adds a cron job.  Interval is in seconds."""
    r.cron[name].func = func
    r.cron[name].interval = interval
    r.cron[name].args = args
    r.cron[name].kwargs = kwargs
    if thread: r.cron[name].type = "thread"
    else:      r.cron[name].type = "process"
    return r.cron[name]

def crondel(name):
    """THEY TOOK OUR JORBS!"""
    del r.cron[name]
    return None

def ps(*args, **kw):
    """Print out a list of all background processes and cron jobs."""
    r.say("\n{0:20} T {1:50} {2:40} | PROCESSES".format("Name","Process","Function"))
    for j in [*r.proc]:
        r.say("{name:20} {t:1} {process:49} {func}".format(name=j,process=repr(r.proc[j].process),func=repr(r.proc[j].func),t=r.proc[j].type[0]))
    r.say("---")
    r.say("{0:20} T {1:3} {2:91} | CRON JORBS".format("Name","Int","Function"))
    for j in [*r.cron]:
        r.say("{name:20} {t:1} {interval:3} {func}".format(name=j,interval=r.cron[j].interval,func=repr(r.cron[j].func),t=r.cron[j].type[0]))

def psx(*args, **kw):
    """Print out a list of all background processes and cron jobs."""
    x=("\n{0:20} T {1:50} {2:40} | PROCESSES\n".format("Name","Process","Function"))
    for j in [*r.proc]:
        x+=("{name:20} {t:1} {process:50} {func}\n".format(name=j,process=escape(repr(r.proc[j].process)),func=escape(repr(r.proc[j].func)),group=r.proc[j].group,t=r.proc[j].type[0]))
    x+=("---\n")
    x+=("{0:20} T {1:3} {2:91} | CRON JORBS\n".format("Name","Int","Function"))
    for j in [*r.cron]:
        x+=("{name:20} {t:1} {interval:3} {func}\n".format(name=j,interval=r.cron[j].interval,func=r.cron[j].func,t=r.cron[j].type[0]))
    return x

# Start the Vixen Cron (lol) .. this has to be a thread, or part of our process.
if not r.proc["VixenCron"]:
    bgthread("VixenCron", crond)
