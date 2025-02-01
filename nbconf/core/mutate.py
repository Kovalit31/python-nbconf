'''
Mutating library.
For using this, in your mod you need to place following construction

__MUTATE = {
    "vars": {
        "variable": type
    },
    "apply" (or "clear"): [[function1], [function2]], # For each stage it's own array
    "casting": [[in_type, out_type, function]]
}

Function signature need to be 'func_name(MutateData, Runtime, Ok | Err)'

@param MUTATE_STAGE_PRESTART - Const variable, that defines stage 0 (prestart)
@param MUTATE_STAGE_POSTSTART - Const variable, that defines stage 1 (poststart)
'''

from nbconf.lib.structs import Ok, Err
# Stages

MUTATE_STAGE_PRESTART = 0
MUTATE_STAGE_POSTSTART = 1

class MutateData:
    '''
    @param _private_data - Can store specific information for specific functions
    @param _stages - Stores functions in arrays, that is splitted by Stages
    @param _mutate_pattern - Mutate variable patterns ("var_name": type)
    @param _mutate_vars - Mutate variables that was registered by current process
    CONTRIBUTORS: BEWARE! Clean _mutate_vars after usage, because it can cause unspecific behaviour
    USERS:
    You can use _private_data for your usage. For example, storing old values for restore.
    But, to not override others data, please add your namespace!
    For example:

    MutateData()._private_data["my_namespace"] = {}

    And then use..
    '''
    _private_data = {}
    _apply_stages = []
    _mutate_pattern = {}
    _mutate_vars = {}
    _clear_stages = []
    _type_casting = {}

    def register_mutate_pattern(self, mutate_pattern: dict):
        '''
        Registers pattern.
        You always need this to do, if you are adding new variables
        @param mutate_pattern - Pattern in style {"variable": type}
        '''
        try:
            self._mutate_pattern.update(mutate_pattern)
        except Exception as e:
            return Err(e)
        return Ok()

    def register_casting(self, in_type, out_type, function):
        '''
        Registeres type casting function.
        Function type need to be **target** type return
        '''
        if not out_type in self._type_casting:
            self._type_casting[out_type] = {}
        if in_type in self._type_casting[out_type]:
            return Err(f"In-type {str(in_type)} is registered for out-type {str(out_type)}! Unregister it before registering again!")
        self._type_casting[out_type][in_type] = function
        return Ok()

    def register_mutate_var(self, mutate_var, data=None):
        '''
        Registeres variable.
        It can be used with only once per command, then you need to empty _mutate_vars.
        You can register each variable. You don't need register unused variables
        @param mutate_var - Variable
        @param data - Data used, if type of variable is not bool
        '''
        if not mutate_var in self._mutate_pattern:
            return Err("Register pattern for {} first".format(mutate_var))
        if self._mutate_pattern[mutate_var] != bool and data is None:
            return Err("Register data for non-boolean type {} cannot be None".format(mutate_var))
        if self._mutate_pattern[mutate_var] == bool:
            self._mutate_vars[mutate_var] = True
            return Ok()
        if not isinstance(data, self._mutate_pattern[mutate_var]):
            if not self._mutate_pattern[mutate_var] in self._type_casting:
                return Err(f"No type casting functions for output type {str(self._mutate_pattern[mutate_var])}")
            if not type(data) in self._type_casting[self._mutate_pattern[mutate_var]]:
                return Err(f"No type casting functions for input type {str(type(data))}")
            try:
                data = self._type_casting[self._mutate_pattern[mutate_var]][type(data)](data) # Only input
            except Exception as e:
                return Err(f"Casting failed: {e}")
        self._mutate_vars[mutate_var] = data
        return Ok()

    def register_apply_mutate(self, stage, func, after=None, before=None):
        '''
        Registers mutate functions.
        @param stage - stage
        @param func - func
        @param after - Not implemented
        @param before - Not implemented
        '''
        if len(self._apply_stages) <= stage:
            for _ in range(stage - len(self._apply_stages) + 1):
                self._apply_stages.append([])
        if after is None and before is None:
            self._apply_stages[stage].append(func)
            return Ok()
        return Err(NotImplementedError("Before and after currently unimplemented"))

    def register_clear_mutate(self, stage, func, after=None, before=None):
        '''
        Registers mutate clearing functions.
        @param stage - stage
        @param func - func
        @param after - Not implemented
        @param before - Not implemented
        '''
        if len(self._clear_stages) <= stage:
            for _ in range(stage - len(self._clear_stages) + 1):
                self._clear_stages.append([])
        if after is None and before is None:
            self._clear_stages[stage].append(func)
            return Ok()
        return Err(NotImplementedError("Before and after currently unimplemented"))

    def apply_mutate(self, stage, runtime, additional=None):
        '''
        Applies mutates for stage.
        Run after pattern registring, function registring, variable registring (for every command) for correct stage
        @param stage - Stage
        @param runtime - Current runtime  
        @param additional - Some additional data
        Additional data is used by POSTSTART mutate, and it is Ok | Err instance
        '''
        if len(self._apply_stages) <= stage:
            # Probably we doesn't registered mutate functions, so abort exec
            return Err("Stage not initializated")
        errored = []
        if stage > 0:
            self.clear_mutate(stage-1, runtime, additional)
        for x in self._apply_stages[stage]:
            try:
                x(self, runtime, additional)
            except Exception as e:
                runtime.print.debug(str(e))
                errored.append(x)
        if errored:
            return Err(f"Errors in these function processing: {str(errored)}")
        return Ok()

    def clear_mutate(self, stage, runtime, additional=None):
        '''
        Clears mutates for stage.
        Run after pattern registring, function registring, variable registring (for every command) for correct stage and applying mutates
        @param stage - Stage
        @param runtime - Current runtime
        @param additional - Some additional data
        Additional data is used by POSTSTART clear mutate, and it is Ok | Err instance
        '''
        if len(self._clear_stages) <= stage:
            # Probably we doesn't registered mutate functions, so abort exec
            return Err("Stage not initializated")
        errored = []
        for x in self._clear_stages[stage]:
            try:
                x(self, runtime, additional)
            except:
                errored.append(x)
        return Ok(errored)
    
    def needs_value_var(self, mutate_var):
        '''
        Returns true, if variable need data, or false, if it is boolean
        '''
        if not mutate_var in self._mutate_pattern:
            return Err("Register pattern for {} firstly".format(mutate_var))
        return Ok(self._mutate_pattern[mutate_var] != bool)