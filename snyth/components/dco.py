# Copyright 2021 Luke Zulauf
# All rights reserved.
"""
Digitally Controlled Oscillator

Our basic sound wave oscillator
"""
import math

import numpy

from snyth import Component, InputPort, OutputPort, Settings


class DCO(Component):
    frequency = InputPort()
    num_samples = InputPort()
    output = OutputPort()
    
    def __init__(self, name, use_local_time=False):
        super().__init__(name)
        
    def generate(self, port_values):
        sample_rate = Settings.instance().sample_rate
        sample_num = 0
        while True:
            frequency = port_values[self.frequency]
            num_samples = port_values[self.num_samples]
            sample_range = range(sample_num, sample_num + num_samples)
            sin_rate = 2.0 * math.pi * frequency / sample_rate
            port_values[self.output] = numpy.sin(
                numpy.array([sample * sin_rate for sample in sample_range],  dtype=numpy.float32))
            sample_num += num_samples
            yield