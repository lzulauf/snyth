# Copyright 2021 Luke Zulauf
# All rights reserved.
from itertools import count
import time

from snyth import Settings
from snyth.logging import logger


class Voice:
    _instance_stack = []
    
    def __init__(self, frequency, algorithm, frame_rate=100):
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
        self._seconds_per_frame = 1/frame_rate
        
    def generate(self, realtime=True, seconds=None):
        """
        If realtime is True, processing is slowed to real time. This is useful for live input when you want the input to line up with the sound.
        If realtime is False, it will process all frames as quickly as possible. This is useful if you have no dynamic inputs or all of your inputs are coming via a premade midi file. The output samples can be generated much faster.
        """
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
        sample_num = 0
        
        # Needed for loops that do a while loop based on cur_time
        self._port_values[self.algorithm.inputs.cur_time] = 0
        self._port_values[self.algorithm.inputs.trigger] = 1
        
        def _inner(cur_time):
            nonlocal sample_num
            total_samples = int(cur_time * Settings.instance().sample_rate)
            num_samples = total_samples - sample_num
            self._port_values[self.algorithm.inputs.num_samples] = num_samples
            self._port_values[self.algorithm.inputs.cur_time] = cur_time
            
            for generator in generators:
                next(generator)
            sample_num = total_samples
            return self._port_values[self.algorithm.outputs.output]

        if realtime:
            return self._realtime_generator(_inner, start_time, seconds)
        else:
            return self._simulated_generator(_inner, seconds)

    def _realtime_generator(self, inner_callback, start_time, seconds):
        while True:
            loop_start = time.perf_counter()
            cur_time = loop_start - start_time
            if seconds and cur_time > seconds:
                cur_time = seconds

            result = inner_callback(cur_time=cur_time)
            loop_end = time.perf_counter()
            loop_duration = loop_end - loop_start
            yield result

            # Be sure to exit after yield values to avoid empty outputs
            if seconds and cur_time >= seconds:
                break

            if loop_duration < self._seconds_per_frame:
                time.sleep(self._seconds_per_frame - loop_duration)
            else:
                logger.warn(f'Overran last frame time. Limit={self._seconds_per_frame}. Used={loop_duration}')

    def _simulated_generator(self, inner_callback, seconds):
        cur_time = 0
        while True:
            if seconds and cur_time > seconds:
                cur_time = seconds

            yield inner_callback(cur_time=cur_time)

            # Be sure to exit after yield values to avoid empty outputs
            if seconds and cur_time >= seconds:
                break

            cur_time += self._seconds_per_frame 
            
    
    @property
    def frame_rate(self):
        return self._frames_per_second
        
    @frame_rate.setter
    def frame_rate(self, frames_per_second):
        self._frames_per_second = frames_per_second
        self._seconds_per_frame = 1/frames_per_second

    #property
    def seconds_per_Frame(self):
        return self._seconds_per_frame

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

    @property
    def trigger(self):
        return self._port_values.get(self.algorithm.inputs.trigger)

    @trigger.setter
    def trigger(self, value):
        self._port_values[self.algorithm.inputs.trigger] = value
