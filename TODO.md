### short [02-909-instrument]

- add env containing sample temperature
- add density condition
- switch instrument to contain sample index not boolean
- add instrument randomise function
- convert 303 block to use while()

### medium

- instrument/seeds/env serialisation
- nine09, three03 subclasses
- refactor banks to use local caching
- perkons grooves
- 303 slide
- 303 slide-to

- decompiler
- digitakt II dual euclidian

### long

- moto upgrade

### thoughts

- density?
  - think euclid selection may be better
- script to minimise bank fixture size?
  - not worth it
- remove Container model?
  - no I think you really need it to encapsulate all the stuff going on
  - and that serialisation, which might cause you to liberate the insides, is a secondary concern
- pattern toggling?
  - think it might be overkill
  - replace with digitakt 2 dual euclidian
- harmonise nomenclature as nine09, three03 etc?
  - not a lot of point
- remove chromatic sampler?
  - no because 303 depends on it
- remove project breaks?
  - no; is complex as includes wash; and might still be useful

### done

- fix failing container test
- explicit spawn patch call
- test removing sustain by setting sustain level to zero, thereby using decay as release

- sample toggling
- default echo wet, feedback values
- euclid pattern
- volume groove
- pass volume
- pass sample index from generator
- 909 note to return trig
- beat generator to return simple quantised beat
- beat generator skeleton
- note() to accept note value
- sample index
- 909 samples
- pass seeds to instrument not rand
- simplify 303 demo
- remove echo defaults
- generator functions
- run demo and see if echo included
- remove machines.yaml and machines.py
- copy 303 instrument to 909 and remove note stuff
- remove env from demo
- copy 303 generator pattern to 909
- revert play function
- define and pass env

```
TypeError: EuclidSequencer.__call__() got multiple values for argument 'rand'
```

- fix 909 container error
- migrate machines.py
- migrate modules.yaml
- refactor Container as SVContainer
- refactor SVPatch as SVTrigPatch
- s3 bank loading to log name of assets
- replace print with logging
- convert classmethods to staticmethods
- remove vitling
- should play be passed seeds or rand? 
  - should rand really be redefined each iteration?
- sample/hold modulator doesn't seem to index into rand (just uses rand.random())
- refactor machines to remove seeds and pass rand instead
- nine09 to self initialise samplers based on generators passed
- initialise nine09 instance
- initialise machine
- randomise machine
- initialise and randomise one machine 
- initialise required seeds 
- initialise pool 
- initialise container
- initialise bank in script
- copy default bank
- remove machines JSON code
- remove slice stuff

