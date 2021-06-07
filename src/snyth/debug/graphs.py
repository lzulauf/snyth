# Copyright 2021 Luke Zulauf
# All rights reserved.
from collections import defaultdict
from itertools import chain

import graphviz
from matplotlib import pyplot
import numpy.fft

from snyth import Settings
from snyth.ports import _InputPort, _OutputPort
from snyth.debug.samples import get_fft, get_samples, get_voice_samples, periods_to_seconds


def graph_output(voice, port=None, periods=None, seconds=1):
    seconds = periods_to_seconds(voice, periods, seconds)
    samples = get_samples(voice, port=port, periods=periods, seconds=seconds)
    seconds_per_sample = seconds / len(samples)
    X = [sample_num * seconds_per_sample for sample_num in range(len(samples))]
    fig = pyplot.figure(figsize=(8*2,4*2))
    pyplot.plot(X, samples, label=f"Waveform of {voice.frequency} Hz Sine Wave")
    pyplot.legend(loc='lower right')
    pyplot.show()
    
    
def graph_fft(voice, port=None, periods=None, seconds=1):
    samples = get_voice_samples(voice, port=port, periods=periods, seconds=seconds)
    fft_results = get_fft(samples)
    Y = fft_results
    X = numpy.fft.fftfreq(Y.size, d=1/Settings.instance().sample_rate)
    fig = pyplot.figure(figsize=(16,5))
    axes = fig.add_axes([0,0,1,1])
    axes.set_xlim(0, 20000)
    pyplot.plot(X, Y, label=f"FFT of {voice.frequency} Hz Sine Wave")
    pyplot.legend(loc='lower right')
    pyplot.show()


def graph_algorithm_graphviz(algorithm):
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
        graph.node(repr(port), port_name)
        
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
