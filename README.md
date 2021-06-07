# Snyth
A Python Music Synthesizer

# Concepts
## Component
A component represents a mathematical operation that can be performed. It can have 0 or more inputs and usually 1 or more outputs. A simple component (Constant) might output a single unchanging value, while a more complex component may scan midi messages, or generate an array of values representing a sine wave.

## Algorithm
Component outputs may be connected to other component inputs. Each Input/Output is known as a Port, while each connection is known as a Patch. An algorithm is simply a network of connected components. Components themselves are stateless and may be re-used in multiple algorithms (if desired).

## Voice
A voice is a single instantiation of a sound. It executes a given algorithm for a specific frequency. When you press a note on a midi keyboard, a Voice produces the sound using the current algorithm.

# Development
## Installation
snyth has several complex package dependencies, both for runtime as well as debugging.
Required:
 - pyaudio
 - pygame
 - numpy
Optional:
 - python-graphviz
 - matplotlib
 - jupyterlab

 Unfortunately, some of these dependencies are too complex for simple pip installation. I have supplied a conda environment.yml file to make setting up a working environment easier.
 ```bash
 $ conda install -n snyth --file environment.yml
 ```

 ## Activating environment
 ```bash
 $ conda activate snyth
 ```
 You can then execute a python environment to interact with snyth
 ```bash
 $ python
 $ ipython
 $ jupyterlab
 ```
