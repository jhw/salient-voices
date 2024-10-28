### short [02-909-instrument]

- 909 note to return trig

### medium

- euclid pattern
- pattern density
- volume groove
- sample switching
- pattern switching

- refactor bank loading to include local caching
- refactor demo naming
- script to minimise bank fixture size
- machine config jsonschema validation

### long

- 303 slides
- perkons grooves
- moto upgrade

### thoughts

- remove chromatic sampler?
  - no because 303 depends on it
- remove project breaks?
  - no; is complex as includes wash; and might still be useful

### done

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

