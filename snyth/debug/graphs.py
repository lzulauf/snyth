# Copyright 2021 Luke Zulauf
# All rights reserved.
from itertools import chain

import graphviz
from matplotlib import pyplot
import numpy
from numpy import fft

from snyth import Settings


def get_samples(voice, port=None, periods=None, seconds=1):
    if port is None:
        port = voice.algorithm.outputs.output
        
    sample_rate = Settings.instance().sample_rate
    frame_length = (sample_rate * periods) // voice.frequency if periods else sample_rate * seconds
    samples = []
    generator = voice.generate()
    while len(samples) < frame_length:
        next(generator)
        new_samples = voice.get_port_value(port)
        if isinstance(new_samples, (numpy.ndarray, list)):
            samples_to_add = min(len(new_samples), frame_length - len(samples))
            samples.extend(new_samples[:samples_to_add].tolist())
        else:
            samples.append(new_samples)
       
    return samples


def get_fft(samples):
    return numpy.abs(fft.rfft(samples))**2 # Convert to power (**2)


def graph_output(voice, port=None, periods=None, seconds=1):
    samples = get_samples(voice, port=port, periods=periods, seconds=seconds)
    fig = pyplot.figure(figsize=(8*2,4*2))
    pyplot.plot(samples, label=f"Waveform of {voice.frequency} Hz Sine Wave")
    pyplot.legend(loc='lower right')
    pyplot.show()
    
    
def graph_fft(voice, port=None, periods=None, seconds=1):
    samples = get_samples(voice, port=port, periods=periods, seconds=seconds)
    fft_results = get_fft(samples)
    Y = fft_results
    X = fft.fftfreq(Y.size, d=1/Settings.instance().sample_rate)
    fig = pyplot.figure(figsize=(16,5))
    axes = fig.add_axes([0,0,1,1])
    axes.set_xlim(0, 20000)
    pyplot.plot(X, Y, label=f"FFT of {voice.frequency} Hz Sine Wave")
    pyplot.legend(loc='lower right')
    pyplot.show()


def graph_voice_graphviz(voice, global_time, local_time):
    return graph_algorithm_graphviz(algorithm=voice.algorithm, voice=voice, global_time=global_time, local_time=local_time)


def graph_algorithm_graphviz(algorithm, voice=None, global_time=None, local_time=None):
    if voice:
        assert global_time is not None
        assert local_time is not None
    all_patches = algorithm.get_all_patches_from()
    all_ports = {
        port
        for from_port, to_ports in all_patches.items()
        for port in chain([from_port], to_ports)
    }
    by_component = defaultdict(set)
    for port in all_ports:
        by_component[port.instance].add(port)
        
    def _port_node(graph, port):
        port_sample = ''
        if voice:
            with voice:
                port_sample = port.get_sample(algorithm, global_time, local_time)
        graph.node(repr(port), f'{port.port_name}\n{port_sample}')
        
    components = {port.instance for port in all_ports} 
    digraph = graphviz.Digraph()
    algorithm_ports = by_component.pop(algorithm.inputs)
    for port in algorithm_ports:
        _port_node(digraph, port)
        
    
    for component, ports in by_component.items():
        cluster = graphviz.Digraph(f'cluster_{component!s}')
        for port in ports:
            _port_node(cluster, port)
        for input_port in (p for p in ports if isinstance(p, _InputPort)):
            for output_port in (p for p in ports if isinstance(p, _OutputPort)):
                cluster.edge(repr(input_port), repr(output_port))
        cluster.body.insert(0, f'\tlabel = "{component.name}"')
        digraph.subgraph(cluster)
    for source, dests in all_patches.items():
        for dest in dests:
            digraph.edge(repr(source), repr(dest))
    return digraph


def graph_algorithm_networkx(algorithm):
    all_patches = algorithm.get_all_patches_from()
    component_ports = defaultdict(set)
    for input_port, connected_port in all_patches:
        component_ports[input_port.instance].add(input_port)
        component_ports[connected_port.instance].add(connected_port)
        
    graph = networkx.DiGraph()
    graph.add_edges_from((a.instance, b.instance) for a, b in algorithm.get_all_patches_from())
    networkx.draw_networkx(graph)
    return graph