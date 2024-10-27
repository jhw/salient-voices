### short [02-909-instrument]

- remove chromatic sampler
- remove vitling

### medium

- complete 909 example
- refactor demo naming
- refactor s3 bank loading
  - needs to include logging
- script to minimise bank fixture size
- replace print with logging
- convert classmethods to staticmethods
- machine config jsonschema validation

### long

- 303 slides
- perkons grooves
- moto upgrade

### thoughts

- remove project breaks?
  - no; is complex as includes wash; and might still be useful

### done

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

