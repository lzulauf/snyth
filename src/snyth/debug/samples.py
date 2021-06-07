# Copyright 2021 Luke Zulauf
# All rights reserved.
import numpy
import numpy.fft

from snyth import Settings


def periods_to_seconds(voice, periods, seconds):
    return periods / voice.frequency if periods else seconds


def get_samples(voice, port=None, periods=None, seconds=1):
    if port is None:
        port = voice.algorithm.outputs.output

    seconds = periods_to_seconds(voice, periods, seconds)
        
    results = []
    generator = voice.generate(realtime=False, seconds=seconds)
    for _ in generator:
        results.append(voice.get_port_value(port))
       
    return results


def get_voice_samples(voice, port=None, periods=None, seconds=1):
    sample_rate = Settings.instance().sample_rate
    frame_length = (sample_rate * periods) // voice.frequency if periods else sample_rate * seconds
    all_samples = numpy.concatenate(get_samples(voice, port=port, periods=periods, seconds=seconds))
    return all_samples[:frame_length]


def get_fft(samples):
    return numpy.abs(numpy.fft.rfft(samples))**2 # Convert to power (**2)
