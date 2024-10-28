### short [02-909-instrument]

- refactor Container as SVContainer
- migrate machines.py
- migrate modules.yaml


### medium

- complete 909 demo
- simplify 303 demo

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

