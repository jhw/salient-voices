## Overview

salient_voices is a Python library for the random evolution and mutation of sound patches, rendered using -

- Sunvox [https://warmplace.ru/soft/sunvox/]
- radiant-voices [https://github.com/metrasynth/radiant-voices]

## Model API

#### Project, Patch

A Project contains a list of Patch objects; a Patch contains a list of Track objects

#### Track

A Track contains state information required for rendering of a particular sound

A Track contains a reference to a Machine, which it can instantiate with the necessary args

#### Machine

A Machine is reponsible for converting Track information into the trigs required by Sunvox; as such is it responsible for rendering a sound, but not for the parameterisation of that render

A Machine is defined in a particular namespace; since Track objects are played sequentially, Tracks which use the same Machine can share the same namespace

A Machine contains a list of Sunvox modules which are used during the render process

#### Container

A Machine must be added to a Container, which is responsible for overall Project rendering to a .sunvox file

Machine instances are very likely to use the same list of modules, since the Track object the Machine objects are bound to are played sequentially and not in parallel

In a similar fashion the render process must aggregate samples which are used by different Sampler objects in the same namespace, and bundle them with the relevant namespaced Sampler module

### Generator

A generator is a function responsible for the precise placement of trigs, rendered using a Machine

A Machine is initialised with a Container ref (remember Machine must belong to a Container)

A Machine's render() method is passed a generator; it calls the generator which it turn yields trigs, which are then added to the underlying Container

