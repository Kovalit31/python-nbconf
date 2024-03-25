'''
Project configuration file
'''
from ..lib.fs import File 
import json
import os
# TODO All

DEFAULT_FILE_NAME = "nbconf.json"

def get_conf(runtime, section: str) -> object:
    full_path = runtime._variables["CONF"] if not os.path.isdir(runtime._variables["CONF"]) else os.path.join(runtime._variables["CONF"], DEFAULT_FILE_NAME)
    try:
        file = File(full_path, touch=False)
        conf = json.loads("".join(file.read().unwrap()).replace("\n", ""))
    except:
        return None
    if not section in conf:
        return None
    return conf[section]

