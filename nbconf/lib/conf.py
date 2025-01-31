'''
Configuration file library
'''
from .fs import File 
import json
import os
# TODO All

DEFAULT_FILE_NAME = "nbconf.json"

def get_conf(runtime, section: str) -> object:
    full_path = runtime.exported_var["CONF"] if not os.path.isdir(runtime.exported_var["CONF"]) else os.path.join(runtime.exported_var["CONF"], DEFAULT_FILE_NAME)
    try:
        file = File(full_path, touch=False)
        conf = json.loads("".join(file.read().unwrap()).replace("\n", "")) # type: ignore
    except:
        return None
    if not section in conf:
        return None
    return conf[section]

def get_flag(runtime, flag: str) -> object:
    flag_section = get_conf(runtime, "flags")
    if flag_section is None:
        return None
    if not flag in flag_section:
        return False
    return True
