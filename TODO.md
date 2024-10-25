### short [02-909-instrument]

- n_ticks, density, temperature args for beats rendering
- randomisation should sit outside machines

### medium

- script to minimise bank fixture size
- replace print with logging
- convert classmethods to staticmethods
- machine config jsonschema validation

- 303 slides
- perkons grooves
 
### long

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

