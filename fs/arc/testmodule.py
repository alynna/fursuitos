import ui
from addict import Dict
import config

def ui_gen():
    u = ui.UIBuilder("testmodule", "Testing module")
    u.req("label", None, "Module to test all control types.")
    u.req("label", """style="color:cyan;" """, "Test of adding attributes to a label.")
    u.run("Run test of controls")
    u.req("color", "eye_l", "Left eye color")
    u.req("color", "eye_r", "Right eye color")
    u.req("checkbox", "synccolor", "Sync eye colors")
    u.req("radio", "synceye", "Eye to sync to", options=["Left","Right"])
    u.req("number", "blink", "Time between blinks", low=3, high=15)
    u.req("text", "test", "What are you?")
    return u.end()

def handler(params):
    return repr(params)
