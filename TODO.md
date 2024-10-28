### short [02-909-instrument]

```
TypeError: EuclidSequencer.__call__() got multiple values for argument 'rand'
```

- populate 909 trig code

### medium

- refactor bank loading to include local caching
- simplify 303 demo
- refactor demo naming
- script to minimise bank fixture size
- machine config jsonschema validation

### gists/music/72x 

- move randomisation from model to cli
- move model into sv

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

