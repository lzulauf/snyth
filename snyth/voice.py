# Copyright 2021 Luke Zulauf
# All rights reserved.
from itertools import count
import time

from snyth import Settings


class Voice:
    _instance_stack = []
    
    def __init__(self, frequency, algorithm, frame_rate=None):
        """
        If frame_rate is specified, each loop processes one frame (in Hz).
        Otherwise, actual time delta is used.
        """
        self._algorithm = algorithm
        self._port_values = {
            algorithm.inputs.voice_frequency: frequency,
            algorithm.inputs.num_samples: 0,
        }
        self._frequency = frequency
        self._frames_per_second = frame_rate
        self._seconds_per_frame = 1/frame_rate if frame_rate else None
        
    def generate(self):
        def _input_port_generator(port):
            patches = self.algorithm.get_patches_to(port)
            for i in count():
                self._port_values[port] = sum(self._port_values[p] for p in patches)
                yield
                
        component_order = self.algorithm.get_component_processing_order()
        generators = []
        for component in component_order:
            generators.extend(_input_port_generator(p) for p in component.get_input_ports())
            generators.append(component.generate(self._port_values))
        
        start_time = time.perf_counter()
        cur_time = start_time
        sample_num = 0
        
        def _loop():
            nonlocal sample_num
            nonlocal cur_time
            if self._seconds_per_frame:
                cur_time += self._seconds_per_frame
            else:
                cur_time = time.perf_counter() - start_time
            total_samples = int(cur_time * Settings.instance().sample_rate)
            num_samples = total_samples - sample_num
            self._port_values[self.algorithm.inputs.num_samples] = num_samples
            self._port_values[self.algorithm.inputs.cur_time] = cur_time
            
            # TODO testing
            # Simulate a trigger release in one second
            self._port_values[self.algorithm.inputs.trigger] = 1 if cur_time < 4 else 0
            for generator in generators:
                next(generator)
            sample_num = total_samples
            return self._port_values[self.algorithm.outputs.output]
            
        return (_loop() for frame_num in count())
    
    @property
    def frequency(self):
        return self._frequency
        
    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency
        self._port_values[self._algorithm.inputs.voice_frequency] = frequency
        
    @property
    def algorithm(self):
        return self._algorithm
    
    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
        
    def get_port_value(self, port):
        return self._port_values[port]
