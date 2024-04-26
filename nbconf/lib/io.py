'''
I/O library
'''

from ..utils import system_is_linux
import sys

if system_is_linux():
    import readline
