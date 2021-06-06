# Copyright 2021 Luke Zulauf
# All rights reserved.
from snyth import Component, OutputPort

class Constant(Component):
    output = OutputPort()
    
    def __init__(self, name, constant):
        super().__init__(name)
        self.constant = constant
        
    def generate(self, port_values):
        port_values[self.output] = self.constant
        while True:
            yield