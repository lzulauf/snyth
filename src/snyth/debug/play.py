# Copyright 2021 Luke Zulauf
# All rights reserved.

import numpy
import pyaudio

from snyth import Settings
from snyth.debug.samples import get_voice_samples

def play_voice_sync(audio, voice, realtime=True, seconds=1):
    frames_per_buffer = Settings.instance().sample_rate//voice.frame_rate
    stream = audio.open(rate=Settings.instance().sample_rate, channels=1, frames_per_buffer=frames_per_buffer, format=pyaudio.paFloat32, output=True)
    generator = voice.generate(realtime=realtime, seconds=seconds)
    for samples in generator:
        written = 0
        num_samples = len(samples)
        while written < num_samples:
            to_write = min(num_samples-written, stream.get_write_available())
            stream.write(samples[written:written+to_write])
            written += to_write
    stream.close()


def play_voice_async(audio, voice, realtime=True, seconds=1):
    generator = voice.generate(realtime=realtime, seconds=seconds)
    samples = numpy.array([], dtype=numpy.float32)
    samples_offset = 0
    def fill_stream(in_data, frame_count, time_info, status_flags):
        nonlocal samples
        nonlocal samples_offset
        result = samples[samples_offset:samples_offset + frame_count]
        samples_offset += frame_count
        while len(result) < frame_count:
            try:
                samples = next(generator)
            except StopIteration:
                return result, pyaudio.paComplete
                
            to_take = frame_count - len(result)
            result = numpy.concatenate((result, samples[:to_take]))
            samples_offset = to_take
        
        return result, pyaudio.paContinue

    frames_per_buffer = Settings.instance().sample_rate//voice.frame_rate
    stream = audio.open(rate=Settings.instance().sample_rate, channels=1, format=pyaudio.paFloat32, output=True, frames_per_buffer=frames_per_buffer, stream_callback=fill_stream, start=True)
    return stream
