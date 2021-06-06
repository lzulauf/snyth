# Copyright 2021 Luke Zulauf
# All rights reserved.

from snyth.ports import _Port, _InputPort, _OutputPort

class Component:
    def __init__(self, name):
        self.name = name
        
    def get_ports(self):
        all_attrs = (
            getattr(self, attr_name)
            for attr_name in dir(self)
            if attr_name.startswith('_')  # Only the _Ports, not Ports
        )
        return (attr for attr in all_attrs if isinstance(attr, _Port))
    
    def get_input_ports(self):
        return (port for port in self.get_ports() if isinstance(port, _InputPort))
            
    def get_output_ports(self):
        return (port for port in self.get_ports() if isinstance(port, _OutputPort))
    
    def generate(self, port_values):
        while True:
            yield
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'
