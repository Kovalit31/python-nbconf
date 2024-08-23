'''
API library
'''
from .structs import Ok
from .io import printf
from .conf import get_conf

def can_disable(*flags):
    '''
    Decorator that can disable function from running, if [configuration file](/nbconf.json) it does
    Useful, if you want to restict command from running by some people
    '''
    def wrap(func):
        def wrapper(*args, **kwargs):
            runtime = args[0] # Declared by API
            for flag in flags:
                enabled = get_conf(runtime, flag)
                if not enabled and enabled is not None:
                    printf("Permanently disabled", runtime=runtime, level="e")
                    return Ok()
            return func(*args, **kwargs)
        return wrapper
    return wrap
