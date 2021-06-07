# Copyright 2021 Luke Zulauf
# All rights reserved.
from snyth import Component, InputPort, OutputPort


class ADSREnvelope(Component):
    """
    A basic envelope using Attack, Decay, Sustain, Release
    """
    cur_time = InputPort()
    trigger = InputPort()
    attack = InputPort()
    decay = InputPort()
    sustain = InputPort()
    release = InputPort()
    
    output = OutputPort()
    
    def generate(self, port_values):
        attack, decay, sustain, release = (port_values[getattr(self, key)] for key in ('attack', 'decay', 'sustain', 'release'))
        last_value = 0
        last_time = 0
        while True:
            trigger = port_values[self.trigger]
            cur_time = port_values[self.cur_time]
            if trigger < 0.5:  # release
                cur_value = max(0, last_value - 1/release * (cur_time-last_time))
            elif cur_time < attack:
                cur_value = min(1, last_value + 1/attack * (cur_time-last_time))
            elif last_value > sustain:
                cur_value = max(sustain, last_value - 1/decay * (cur_time-last_time))
            else:
                cur_value = sustain
                
            last_time = cur_time
            last_value = cur_value
            port_values[self.output] = last_value
            yield
                
