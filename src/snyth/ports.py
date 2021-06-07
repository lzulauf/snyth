# Copyright 2021 Luke Zulauf
# All rights reserved
"""
Ports represent connection points that algorithms can use to define a component patch graph.

There are two types of port: InputPort and OutputPort

Both provide the same functionality but use different types for easy disambiguation of their intended use.

Each port is implemented as a descriptor with the value being an _InputPort or _OutputPort.
"""


class _Port:
    def __init__(self, instance, port_name):
        self.port_name = port_name
        self.instance = instance
        
    def __repr__(self):
        return f'{self.__class__.__name__}({self.instance.name}, {self.port_name})'

            
class _InputPort(_Port):
    pass
           
        
class _OutputPort(_Port):
    pass


class BasePort:   
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'   
        
    def __get__(self, instance, owner):
        if not hasattr(instance, self.private_name):
            setattr(instance, self.private_name, self._port_factory(instance))
        return getattr(instance, self.private_name)
    
    def _port_factory(self, instance):
        raise NotImplementedError
            
            
class InputPort(BasePort):
    def _port_factory(self, instance):
        return _InputPort(instance, self.name)

            
class OutputPort(BasePort):
    def _port_factory(self, instance):
        return _OutputPort(instance, self.name)
        
