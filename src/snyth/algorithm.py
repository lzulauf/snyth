# Copyright 2021 Luke Zulauf
# All rights reserved.

from collections import defaultdict
from snyth.component import Component
from snyth.ports import InputPort, OutputPort

"""
An algorithm stores all the patches between components, leaving the components themselves stateless.

Components can be used in multiple algorithms, with each component wiring the components differently.
"""
from collections import defaultdict


class AlgorithmInputs(Component):
    voice_frequency = OutputPort()
    num_samples = OutputPort()
    cur_time = OutputPort()
    sample_rate = OutputPort()
    trigger = OutputPort()

    
class AlgorithmOutputs(Component):
     output = InputPort()

        
class Algorithm:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self._patches_to = defaultdict(set)
        self._patches_from = defaultdict(set)
        self.inputs = AlgorithmInputs(f'{name}_inputs')
        self.outputs = AlgorithmOutputs(f'{name}_outputs')
        
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def patch(self, from_port, to_port):
        self._patches_to[to_port].add(from_port)
        self._patches_from[from_port].add(to_port)
        
    def unpatch(self, from_port, to_port):
        self._patches_to[to_port].remove(from_port)
        self._patches_from[from_port].remove(to_port)
        
    def get_all_connections_to(self):
        result = defaultdict(set)
        for to_port, from_ports in self._patches_to.items():
            result[to_port.instance] |= {from_port.instance for from_port in from_ports}
        return result
    
    def get_all_connections_from(self):
        result = defaultdict(set)
        for from_port, to_ports in self._patches_from.items():
            result[from_port.instance] |= {to_port.instance for to_port in to_ports}
        return result
        
    def get_patches_to(self, to_port):
        return self._patches_to[to_port]
    
    def get_patches_from(self, from_port):
        return self._patches_from[from_port]
    
    def get_all_patches_to(self):
        return self._patches_to
    
    def get_all_patches_from(self):
        return self._patches_from
    
    def get_component_processing_order(self):
        from_connections = self.get_all_connections_from()
        to_connections = self.get_all_connections_to()
        
        root_components = from_connections.keys() - to_connections.keys()
        
        components_to_process = list(root_components)
        component_processing_order = []
        while components_to_process:
            component = components_to_process.pop()
            component_processing_order.append(component)
            for to_component in from_connections[component]:
                to_connections[to_component].remove(component)
                if not to_connections[to_component]:
                    components_to_process.append(to_component)

        return component_processing_order
