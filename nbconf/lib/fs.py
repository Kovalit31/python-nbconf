'''
Filesystem library
'''
from ..utils import printf
from ..utils.structs import Err, Ok, Result

import os
import shutil

class FsObject:
    path = ""
    file = False

    def __init__(self, path: str) -> None:
        self.path = os.path.normpath(os.path.realpath(path))

    def __eq__(self, value) -> bool:
        if not isinstance(value, FsObject):
            return False
        return self.file == value.file and self.path == value.path

    def isdir(self) -> bool:
        return not self.file

    def isfile(self) -> bool:
        return self.file

class File(FsObject):
    '''
    File representation class (high-level abs)
    '''
    
    file = True

    def __init__(self, path: str, touch=True) -> None:
        super().__init__(path)
        if not os.path.exists(self.path):
            if not touch:
                raise OSError("File not exists!")
            self.clear()
        elif os.path.isdir(self.path):
            printf(f"Path is directory: '{path}'!", level='f')

    def clear(self) -> Result:
        try:
            open(self.path, "w", encoding="utf-8").close()
            return Ok()
        except Exception as e:
            return Err(Exception(f"Can't clear: {str(e)}"))

    def read(self) -> Result:
        try:
            f = open(self.path, "r", encoding="utf-8")
            if not f.readable():
                f.close()
                return Err(f"Can't read file: not readable: '{self.path}'")
            s = f.readlines()
            f.close()
            return Ok(s)
        except Exception as e:
            return Err(f"Read error: {str(e)}")
    
    def write(self, data: list, append=True) -> Result:
        try:
            _w = "\n".join(data) if isinstance(data, list) else str(data)
            f = open(self.path, "a" if append else "w", encoding="utf-8")
            if not f.writable():
                f.close()
                return Err(f"Can't read file: not readable: '{self.path}'")
            f.write(_w)
            f.close()
            return Ok()
        except Exception as e:
            return Err(f"Write error: {str(e)}")

    def remove(self) -> Result:
        try:
            os.remove(self.path)
            del(self)
            return Ok()
        except Exception as e:
            return Err(f"Remove error: {str(e)}")

class Dir(FsObject):
    '''
    Directory representation class (high-level abs)
    '''

    def __init__(self, path: str):
        super().__init__(path)
        if not os.path.exists(self.path):
            self.create()
        elif os.path.isfile(self.path):
            printf(f"Path is file: '{self.path}'!", level='f')

    def create(self) -> Result:
        if os.path.exists(self.path):
            return Ok()
        try:
            os.makedirs(self.path)
            return Ok()
        except Exception as e:
            return Err(f"Create error: '{str(e)}'!")
   
    def add_file(self, name: str) -> Result:
        _norm = os.path.normpath(name)
        if os.path.isabs(_norm):
            if os.path.exists(_norm):
                return Err("File exists: '{_norm}'!")
            return Ok(File(name))
        _full = os.path.normpath(os.path.join(self.path, name))
        if os.path.exists(_full):
             return Err("File exists: '{_norm}'!")
        return Ok(File(_full))

    def add_dir(self, name: str):
        _norm = os.path.normpath(name)
        if os.path.isabs(_norm):
            if os.path.exists(_norm):
                return Err("Directory exists: '{_norm}'!")
            return Ok(Dir(name))
        _full = os.path.normpath(os.path.join(self.path, name))
        if os.path.exists(_full):
             return Err("Directory exists: '{_norm}'!")
        return Ok(Dir(_full))
    
    def list(self) -> Result:
        try:
            return Ok(os.listdir(self.path))
        except Exception as e:
            return Err(f"List error: {str(e)}")

    def remove(self) -> Result:
        try:
            shutil.rmtree(self.path)
            del(self)
            return Ok()
        except Exception as e:
            return Err(f"Remove error: {str(e)}")

