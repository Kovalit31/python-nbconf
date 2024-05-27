'''
API library
'''
from ..utils.structs import Ok
from ..utils import printf
from .conf import get_conf

def can_disable(flag: str):
    def wrap(func):
        def wrapper(*args, **kwargs):
            runtime = args[0] # Declared by API
            enabled = get_conf(runtime, flag)
            if not enabled and enabled is not None:
                printf("Permanently disabled", runtime=runtime, level="e")
                return Ok()
            return func(*args, **kwargs)
        return wrapper
    return wrap
