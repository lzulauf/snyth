# Copyright 2021 Luke Zulauf
# All rights reserved.
from snyth import Component, InputPort, OutputPort
from snyth.components.dco import DCO
from snyth.components.adsr_envelope import ADSREnvelope


class SubtractiveOperator(Component):
    trigger = InputPort()
    cur_time = InputPort()
    base_frequency = InputPort()
    frequency_multiplier = InputPort()
    num_samples = InputPort()  # This should really be communicated via other means than port connections
    amplitude = InputPort()
    attack = InputPort()
    decay = InputPort()
    sustain = InputPort()
    release = InputPort()
    
    output = OutputPort()
    
    def __init__(self, name):
        super().__init__(name)
        self.dco = DCO(f'{name}_dco')
        self.adsr_envelope = ADSREnvelope(f'{name}_envelope')
        
        # TODO how to manage hardwired connections?
        
    def generate(self, port_values):
        dco_generator = self.dco.generate(port_values)
        envelope_generator = self.adsr_envelope.generate(port_values)
        def _prep_inputs():
            port_values[self.adsr_envelope.cur_time] = port_values[self.cur_time]
            port_values[self.adsr_envelope.trigger] = port_values[self.trigger]
            port_values[self.adsr_envelope.attack] = port_values[self.attack]
            port_values[self.adsr_envelope.decay] = port_values[self.decay]
            port_values[self.adsr_envelope.sustain] = port_values[self.sustain]
            port_values[self.adsr_envelope.release] = port_values[self.release]
            port_values[self.dco.frequency] = port_values[self.base_frequency] * port_values[self.frequency_multiplier]
            port_values[self.dco.num_samples] = port_values[self.num_samples]
            
        # Have to prep inputs prior to iterating generators
        _prep_inputs()
        for i in zip(dco_generator, envelope_generator):
            port_values[self.output] = (
                port_values[self.dco.output] * 
                port_values[self.adsr_envelope.output] * 
                port_values[self.amplitude]
            )
            yield
            # We then have to prep inputs prior to the next iteration
            _prep_inputs()
