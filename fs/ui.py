from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys
import urllib.parse as parser
from config import c, mkmutual
import config
import r
from addict import Dict
import math
from fsts import psx
from html import escape
from collections import OrderedDict
import pprint
import traceback

def header(title=None, bgcolor="#222222", fgcolor="#FFFFFF"):
    # Open HTML
    if title is not None: title += " - "
    else: title = ""
    x="""<html><head><title>{title}{uititle}</title><meta name="viewport" content="width=device-width, initial-scale=1.0">""".format(title=title,uititle=c.ui.title)
    # Add default CSS
    try:
        with open("www/default.css") as f:
            x+=f.read()
    except:
        pass    
    # Add default javascript
    try:
        with open("www/default.js") as f:
            x+=f.read()
    except:
        pass
    x+="""<body bgcolor="{bgcolor}"><font color="{fgcolor}">""".format(bgcolor=bgcolor,fgcolor=fgcolor)
    return x

def footer():
    # Close HTML
    return "<hr>Rendered by FursuitOS v{version} (C) 2018 Alynna Trypnotk, GPL3</font></body></html>{0:512}".format("",version=r.version)
    
def message(err, x):
    if err == 403:      error = "Module access disabled"
    elif err == 404:    error = "Module not found"
    elif err == 500:    error = "Module raised exception."
    elif err == 503:    error = "Module has no handler."
    else:               error = "Kernel panic.  I can't believe they gave you a starship."
    return header("{err}: {error}".format(err=err, error=error),bgcolor="#220000")+\
            """<h2><font color="red">{err}</font>: {error}</h2><p>{x}</p>""".format(err=err,error=error,x=x)+\
            footer()

def save_to_conf(module, src):
    def s(x):
        try:
            return src[module+"."+x][0]
        except:
            return None
    typ = r.ui.progs[module]
    conf = c.cfg[module]
    for j in [*typ]:
        if typ[j] == "label":
            pass
        if typ[j] == "action":
            pass
        if typ[j] == "multi":
            conf[j] = src[module+"."+j]
        elif typ[j] == "checkbox":
            if s(j) is not None:
                conf[j] = True
            else:
                conf[j] = False
        elif typ[j] == "number" or typ[j] == "range":
            try:
                conf[j] = int(s(j))
            except:
                conf[j] = 1
        else:
            conf[j] = str(s(j))
    config.save()


class UIBuilder(object):
    def __init__(self, name, label=None):
        self.name = name
        try:    del r.ui.progs[name]
        except: pass
        if label is None:
            self.x="""<form action="/{name}" method="get"><fieldset><legend>{name}</legend><table width="100%">""".format(name=self.name)
        else:
            self.x="""<form action="/{name}" method="get"><fieldset><legend>{name} : {label}</legend><table width="100%">""".format(name=self.name,label=label)
    def run(self, label):
        self.x+="""<tr><td><input class="button" type="submit" width="100%" value="{label}"></td></tr>""".format(name=self.name,label=label)
    def req(self, typ, conf, label, **kw):
        try:
            cval=eval("c.cfg.{name}.{conf}".format(name=self.name,conf=conf))
        except Exception as e:
            cval=e
        if cval == {}: cval = ""
        if not (typ == "label" or typ == "action"):
            r.ui.progs[self.name][conf]=typ
        if typ == "checkbox":
            if not cval or cval == "False":
                self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}"></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval)
            else:
                self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}" checked></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval)
        elif typ == "color": 
            self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}"></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval)
        elif typ == "number":
            y = []
            try: y+=['min="{low}"'.format(low=kw["low"])]
            except: pass
            try: y+=['max="{high}"'.format(high=kw["high"])]
            except: pass
            try: y+=['step="{step}"'.format(step=kw["step"])]
            except: pass
            y=str(" ".join(y))
            self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}" {y}></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval, y=y)
        elif typ == "range":
            y = []
            try: y+=['min="{low}"'.format(low=kw["low"])]
            except: pass
            try: y+=['max="{high}"'.format(high=kw["high"])]
            except: pass
            try: y+=['step="{step}"'.format(step=kw["step"])]
            except: pass
            y=str(" ".join(y))
            self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}" {y}></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval, y=y)
        elif typ == "label":
            if conf is None:
                self.x+="""<tr><td><p>{label}</p></td></tr>""".format(label=label)
            else:
                self.x+="""<tr><td><p {conf}>{label}</p></td></tr>""".format(label=label, conf=conf)
        elif typ == "action":
                self.x+="""<tr><td><a class="lbutton" href="/{name}?action={conf}">{label}</a></td></tr>""".format(label=label,name=self.name,conf=conf)
        elif typ == "text": 
            self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}"></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval)
        elif typ == "radio": 
            self.x+="""<tr><td><fieldset><legend>{label}</legend>""".format(label=label)
            for j in kw["options"]:
                if cval == j:
                    self.x+="""<input name="{name}.{conf}" id="{j}" type="{typ}" value="{j}" checked> {j} &nbsp;&nbsp;""".format(name=self.name, conf=conf, j=j, typ=typ)
                else:
                    self.x+="""<input name="{name}.{conf}" id="{j}" type="{typ}" value="{j}"> {j} &nbsp;&nbsp;""".format(name=self.name, conf=conf, j=j, typ=typ)
            self.x+="""</fieldset></td></tr>"""
        elif typ == "select": 
            self.x+="""<tr><td><fieldset><legend>{label}</legend>""".format(label=label)
            self.x+="""<select name="{name}.{conf}" id="{conf}">""".format(name=self.name,conf=conf)
            for j in kw["options"]:
                if cval == j:
                    self.x+="""<option value="{j}" selected>{j}</option>""".format(j=j)
            for j in kw["options"]:
                if not cval == j:
                    self.x+="""<option value="{j}">{j}</option>""".format(j=j)
            self.x+="""</select></fieldset></td></tr>"""
        elif typ == "multi": 
            self.x+="""<tr><td><fieldset><legend>{label}</legend>""".format(label=label)
            self.x+="""<select name="{name}.{conf}" id="{conf}" multiple>""".format(name=self.name,conf=conf)
            for j in kw["options"]:
                if j in eval("c.cfg.{name}.{conf}".format(name=self.name,conf=conf)):
                    self.x+="""<option value="{j}" selected>{j}</option>""".format(j=j)
            for j in kw["options"]:
                if not j in eval("c.cfg.{name}.{conf}".format(name=self.name,conf=conf)):
                    self.x+="""<option value="{j}">{j}</option>""".format(j=j)
            self.x+="""</select></fieldset></td></tr>"""
        else:
            self.x+="""<tr><td><p>{label}&nbsp;<input name="{name}.{conf}" type="{typ}" value="{cval}"></p></td></tr>""".format(name=self.name, conf=conf, label=label, typ=typ, cval=cval)
    def end(self):
        return self.x+"</table></fieldset></form>"
    
class MainPage(object):
    def render():
        x="""<table width="100%">"""
        x+=MainPage.render_title()
        x+=MainPage.render_status()
        x+=MainPage.render_mutuals()
        x+=MainPage.render_progs()
        x+=MainPage.render_debugs()
        x+=MainPage.render_motd()
        x+="</table>"
        r.ui.status = None
        return x
    def render_title():
        x="""<tr><td><font size="+2">{uititle} : {part}</font></td></tr>""".format(uititle=c.ui.title,part=c.part)
        return x
    def render_status():
        if r.ui.status:
            x="""<tr><td bgcolor="{bgcolor}"><fieldset><legend>Status Update</legend>{status}</fieldset></td></tr>""".format(status=r.ui.status,bgcolor=(r.ui.status_bg if r.ui.status_bg else "#004000"))
        else: x=""
        return x
    def render_mutuals():
        x="""<tr><td bgcolor="#400040"><fieldset><legend>Fursuit parts</legend>"""
        x+="""<a class="lbutton" href="/">{label}</a>""".format(label=c.part)
        if c.mutuals:
            for j in [*c.mutuals]:
                x+="""<a class="lbutton" href={mutual}>{label}</a>""".format(mutual=mkmutual(c.mutuals[j]),label=j)
            x+="</fieldset></td></tr>"
        return x
    def render_progs():
        x=""
        # Search for mods and sort them by loading order.
        if [*r.fs]:
            tmp = {}
            for j in [*r.fs]:
                if not c.mod[j].render == {}:
                    tmp[j] = c.mod[j].render
                else:
                    tmp[j] = (2 ** 24)
            l = (OrderedDict(sorted(tmp.items(), key=lambda q: q[1]))).keys()
            del tmp
        for j in l:
            try:
                y = r.fs[j].ui_gen()
            except AttributeError:
                y = """<fieldset><legend>{0}</legend>&#x1F98A; No UI &#x1F98A;</fieldset>""".format(j)
            except Exception as e:
                y = e
            x+="<tr><td>{y}<br /></td></tr>".format(y=y)
        return x
    def render_debugs():
        x="""<tr><td bgcolor="#400040"><fieldset><legend>Debug Nodes</legend>"""
        x+="""<a class="lbutton" href="/ps" target="_debug">Process status</a>&nbsp;&nbsp;"""
        x+="""<a class="lbutton" href="/log" target="_debug">System log</a>&nbsp;&nbsp;"""
        x+="""<a class="lbutton" href="/reg" target="_debug">Registry</a>&nbsp;&nbsp;"""
        x+="""<a class="lbutton" href="/reload">Reload OS</a>&nbsp;&nbsp;"""
        x+="</fieldset></td></tr>"
        return x
    def render_motd():
        x="""<tr><td bgcolor="#004040"><fieldset><legend>MOTD</legend>"""
        with open("www/motd.html") as f: x+=f.read()
        x+="</fieldset></td></tr>"
        return x

class Dispatcher(object):
    def handler(path, params):
        try:
            if not callable(r.fs[path].handler):
                return 404, "No handler found for {x}.  Module requires a handler.".format(x=path)
            try:
                params["action"][0]
            except:
                save_to_conf(path,params)
            r.ui.status = r.fs[path].handler(params)
            return 200, "OK"
        except Exception as e:
            return 500, "Handler in module {x} threw exception.<br /><fieldset><legend>{e}</legend>{bige}</fieldset>".format(
                x=path,e=sys.exc_info()[1],bige=escape(traceback.format_exc()))

# HTTPRequestHandler class
class FursuitUI(BaseHTTPRequestHandler):
    def render_page(self, title, body):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(header(title)+body+footer(),"utf-8"))
    def render_page_raw(self, code, body):
        self.send_response(code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(body,"utf-8"))
    def main(self):
        self.render_page(None, MainPage.render())
    def log_message(self, fmt, *args):
        r.say("[HTTP@{0}] {1}".format(self.client_address[0],(fmt % args)))
    def do_GET(self):
        """Why am I doing this in all get requests?
        Because I want to be able to save arbitrary URLs that change my fursuit state."""
        try:
            module, params = self.path.split("?",1)
        except:
            module, params = self.path, None

        module = module[1:] 
        params = parser.parse_qs(params,keep_blank_values=True)
        if len(module) == 0: module = "main"
        if module == "main": self.main()
        elif module == "log":
            with open("/run/shm/fursuitos.log") as f:
                self.render_page("Debug log", """<div style="white-space: pre-wrap; font-family:monospace;">"""+f.read()+"</div>")
        elif module == "ps":
            self.render_page("Process stats", """<div style="white-space: pre-wrap; font-family:monospace;">"""+psx()+"</div>")
        elif module == "reg":
            self.render_page("Registry", """<div style="white-space: pre-wrap; font-family:monospace;">"""+escape(r.regdump())+"</div>")
        elif module == "reload":
            self.render_page("Reload", """<p>Reloading OS, may be unavailable for a few seconds...</p><a href="/" class="lbutton">Home</a>""")
            os.system("""bash -c "sleep 1; cd /fs; ./fursuitos.py" &""")
            os.system("""pkill -9 -f "python3.*fursuitos" """)
            sys.exit(1)
        elif module == "favicon.ico":
            self.send_response(200)
            self.end_headers()
            with open("www/favicon.ico","rb") as f:
                self.wfile.write(bytes(f.read()))
        elif module == "robots.txt":
            self.send_response(200)
            self.end_headers()
            with open("www/robots.txt","r") as f:
                self.wfile.write(bytes(f.read(),"utf-8"))
        else:
            code, payload = Dispatcher.handler(module,params)
            if code >= 300:
                self.render_page_raw(code, message(code, "[Yerf] {err} <br \>[DEBUG] Here's your parameters back:<br />&nbsp;{y}".format(err=payload,x=module,y=repr(params))))
            else:
                self.main()
        return
