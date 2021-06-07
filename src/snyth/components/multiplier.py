# Copyright 2021 Luke Zulauf
# All rights reserved.
from snyth import Component, InputPort, OutputPort


class Multiplier(Component):
    a = InputPort()
    b = InputPort()
    output = OutputPort()
    
    def generate(self, port_values):
        for i in count():
            port_values[self.output] = port_values[self.a] * port_values[self.b]
            yield