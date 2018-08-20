# fs/config.py - load the configuration for this part of the fursuit.
# Fursuit configuration node.

# He's an eevee looking to serialize an object in YAML.
# She's a sylveon trying to make a programmable fursuit.
# ... They fight crime.
from camel import Camel, CamelRegistry
# Dictionaries the way I like them.
from addict import Dict  
# This module will also discover WHO WE ARE.
import socket
import r
caramel = CamelRegistry()

# Configure the fursuit part here.
defaults = """
name: alynna
part: tails
node: 241
mutuals:
  head: https://head.fursuit.kitsunet.net/
ui:
  title: "Alynna's Fursuit"
  bind: 0.0.0.0
  port: 80
iot:
  host: fursuit.kitsunet.net
  port: 8472
hw:
  led:
    r:
      index: 0
      interface: neopx
    o:
      index: 1
      interface: neopx
    g:
      index: 2
      interface: neopx
    b:
      index: 3
      interface: neopx
    i:
      index: 4
      interface: neopx
    v:
      index: 5
      interface: neopx
"""
# Initialization
c = Dict(Camel([caramel]).load(defaults))

def save():
    """Save config to fursuit.yaml"""
    global c
    try:
        with open("/boot/FursuitOS/fursuit.yaml","w") as f:
            f.write(Camel([caramel]).dump(c.to_dict()))
        return True
    except:
        return False
        
def load():
    """Load config from fursuit.yaml"""
    global c
    try:
        with open("/boot/FursuitOS/fursuit.yaml") as f:
            c = Dict(Camel([caramel]).load(f.read()))
        return True
    except:
        c = Dict(Camel([caramel]).load(defaults))
        return False
        
def reset():
    """Reset to default configuration."""
    global c
    c = Dict(Camel([caramel]).load(defaults))
    save()

def mkmutual(node):
    if isinstance(node, int):
        who_are_they=whoami.split(".")[0:3] + [str(node)]
        return "http://{0}.{1}.{2}.{3}/".format(who_are_they[0],who_are_they[1],who_are_they[2],who_are_they[3])
    else:
        return node
    
if load():
    r.say("[FSConfig] Configuration loaded.")
else:
    save()
    r.say("[FSConfig] Reset Config.")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("1.1.1.1", 53))
whoami = s.getsockname()[0]
s.close()
r.say(Camel([caramel]).dump(c.to_dict()))
