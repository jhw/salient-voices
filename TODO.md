### short

- why is trig.sample_mod required?

### medium

- adjust algos for ticks per beat
  - does sunvox support per- pattern speeds?

- modifiers model
- 303 slide, slide- to
- decompiler
- digitakt II dual euclidian

### gists 

- sunvox drum 909
- arranger (git?)
- trimming, repeating, reversing 
- resample arranger
- breaks and wash
- live looper

### long

- moto upgrade

### thoughts

- test for md5 checking in utils/banks?
  - not clear it's worth it
- base classes for 303, 909?
  - no because not clear how defaults in a superclass should then be handled
  - also smacks of over- optimisation
- include local caching in banks?
  - no it feels like this is really an app level thing
  - feels like there are situations where you wouldn't in fact want or need it
- refactor demos as tests?
  - no because they are really demos
- script to minimise bank fixture size?
  - not worth it
- remove Container model?
  - no I think you really need it to encapsulate all the stuff going on
  - and that serialisation, which might cause you to liberate the insides, is a secondary concern
- pattern toggling?
  - think it might be overkill
  - replace with digitakt 2 dual euclidian
- remove chromatic sampler?
  - no because 303 depends on it

### done

- sync_banks to wrap keys/diff/sync logic
- use **env
- something more pythonic for pattern indexing
- pass all modules to trig_groups

- 303 >> ERROR: SVChromaticSampler takes a single- sample pool only

- add back sample mod for mikey 303
- investigate samplers being populated with every sample
- rename main script as demo.py
- nine09/samples demo doesn't need re
- auto- capitalises namespace
- why are all patterns rendering the same

```
ERROR: modules names are not unique
```

- new sv 0.3 randomiser 
- move sampleref into banks
- import SVSampleRef as SVSample
- match to take matcher function
- move subset to banks from bank
- cast pool passed to subset
- cast sample
- don't cast sample and see what happens
- remove vitling, wolgroove
- rename filter_tag as match
- remove pool.tags
- bank.subset functionality
- sample tag stuff in banks spawn_pool should be moved into SVSample
- rename filter_by_tag as filter
- check tag filtering returns a new bank
- move load_banks into SVBanks
- rename zip_file, wav_file
- remove SVBank support for file loading
- move colours to utils
- rename play() as render()
- banks/utils diff_keys to do filesize checking
- remove RuntimeError catching in tests
- refactor tests/utils/banks.py
- sync|load_banks
- perkons grooves
- remove serialisation classes
- rename demo outputs
- nine09, three03 subclasses
- 303 volume groove
- convert 303 block to use while()
- refactor beats to call all random stuff at start
- add beat density
- give env a blank default arg?
- add env containing sample temperature
- rename InstrumentBase as SVInstrumentBase
- extend container classes
- remove wash and breaks
- add instrument randomise function
- switch instrument to contain sample index not boolean
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

