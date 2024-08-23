'''
Structures and classes
'''

from dataclasses import dataclass

# =============================
#          Exceptions
# =============================

class InternalError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class LanguageError(InternalError):
    pass


# ====================
#        Result
# ====================

class Result:
    '''
    Result - Rust like class for result access
    '''
    def __init__(self) -> None:
        self._ok = True
        self._err = LanguageError("Result design error")
        self._data = None

    def is_ok(self) -> bool:
        '''
        Returns True, if result is Ok
        '''
        return self._ok

    def is_err(self) -> bool:
        '''
        Return True, if result is Err
        '''
        return not self._ok
    
    def unwrap(self) -> object:
        '''
        Potencially unwraps Err, if it exists, or return Ok data
        '''
        if self.is_err():
            raise self._err
        return self._data

class Ok(Result):
    '''
    Ok class of Result
    '''
    def __init__(self, *packet_data) -> None:
        super().__init__()
        self._ok = True
        if (a:=len(packet_data)) == 0:
            self._data = None
        elif a == 1:
            self._data = packet_data[0]
        else:
            self._data = packet_data

class Err(Result):
    '''
    Err class of Result
    '''
    def __init__(self, error: object = None) -> None:
        super().__init__()
        if isinstance(error, BaseException):
            self._err = error
        elif isinstance(error, str):
            self._err = Exception(error)
        else:
            self._err = Exception("Unknown error")

@dataclass
class Token:
    type: str
    value: object
    line: int
    column: int

class RValue():
    def __init__(self, data):
        self.data = data

class Empty():
    pass

