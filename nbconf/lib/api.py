'''
API library
'''
from .structs import Ok
from .conf import get_flag

def can_disable(*flags):
    '''
    Decorator that can disable function from running, if [configuration file](/nbconf.json) it does
    Useful, if you want to restict command from running by some people
    '''
    def wrap(func):
        def wrapper(*args, **kwargs):
            runtime = args[0] # Declared by API
            for flag in flags:
                is_flag = get_flag(runtime, flag)
                if is_flag and is_flag is not None:
                    runtime.print.error("Permanently disabled")
                    return Ok()
            return func(*args, **kwargs)
        return wrapper
    return wrap

def can_enable(*flags):
    '''
    This is as can_disable functions, but vice versa
    '''
    def wrap(func):
        def wrapper(*args, **kwargs):
            runtime = args[0] # Declared by API
            for flag in flags:
                is_flag = get_flag(runtime, flag)
                if not is_flag or is_flag is None:
                    runtime.print.error("Permanently disabled")
                    return Ok()
            return func(*args, **kwargs)
        return wrapper
    return wrap