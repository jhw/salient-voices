### short [01-sv-note]

- instruments methods to only set trig i if it's non zero, and then as an offset 
- new sv note class at container or instrument level with trigs field
- instrument to return sv note class
- add sv note render(i) skeleton 
- add update i method to trigs 
- add base trig class
- generator to call render(i) on note
- remember to clone notes 

### medium

- pico sequences [notes]

- chromatic sample distribution [notes]

- pico play mode
- grooves
- demos/909

### features

##### 303, 909

- fills [notes]

##### 303

- filter decay
- pitch bend
- slide to note

##### 909

- off- beat samples

### long

- moto upgrade

### thoughts

- turn off export debugging?
  - not possible it seems
- distortion?
  - dirties the notes unfortunately
- SVNoteTrig.note should be named offset if it's an offset?
  - is fine
- sv project player?
  - not sure you need it
- export test should use wavfile to validate output properties?
  - probably not worth it
- colour mutation?
  - not worth it
- tidal syntax?
  - not clear you need it, if it's really a performance thing

### done

- remove i arg being passed to instrument methods 
- add trig clone methods 
- add default i = 0 arg to trigs 
- container test
- distribute colours
- bank concatenation utility
- add individual seeds
- test distortion
- test 240bpm
- check raw 303 VCO SQR.wav sound vs C5 midpoint
- add saw wave to 303 demo
- check 303 demo still works
- rename load_files as load_wav_files
- rename load|dump_zip as load|dump_zip_file
- replace single shot in tests
- remove single shot
- replace single shot in demos
- refactor single shot bank as file loading bank utility
- test slot sampler code with Euclid gist 
- check refactored samplers work with 303 demo, particularly offset code 
- rename lookup as index of
- check use of note in tests (should be offset where sampler concerned)
- change demo to use offset
- refactor SingleSampler refs
- refactor trig code to use note as offset in the presence of chromatic sampler only
- slot sampler to override root_notes with slot position
- chromatic sampler to override root_notes with mid points
- add notes re chromatic mid point assumptions
- lookup function to reference root_notes
- add root_notes property to base sampler
- move existing constructor to base constructor, with repitch arg
- add new slot and chromatic samplers, passing repitch arg to superclass
- remove single slot sampler
- pass rand into generator
- reverb
- consider multiple seeds
- initialise bassline with seed 
- pass seed from command line
- specify module default parameters as instrument constructor params
- add echo
- three03 should be initialised with sample
- randomise filter level
- refactor demos/303 to use generator pattern
- extend bassline function to include state
- define simple stateless bassline function in demo
- demo to execute bassline
- add instrument play function, attaching trigs
- remove trig- attaching decorator
- remove single slot offset
- refactor nine09 demo to use three03 patterns
- dev/three03_generator.py [notes]
- old pop colours
- add Tidal euclid patterns
- test pool.filter_by_tags
- test pool.tags
- always recast sample as SVSample
- samples should be inserted into pool as SVSample instances
  - remove recasting in banks code
- add check for type in banks spawn_pool test
- new PoolTest class
- add back tag related code to pool (look in euclid cli)
- replace instances of sample.split("/") with casting of class and use of properties
- refactor spawn_pool to use new sample format
- new svsample class extending string
- add svsample properties
- rip out tags stuff from pool
- file utils
- bank tag code
- SVBanks spawn_pool code doesn't take into account custom SVPool class in euclid cli
- number of lines in patch
- single slot sampler to take repitch arg
- banks should really not be a list
- banks.spawn_pool
- bjorklund
- add online check
- slice_wav_custom should be renamed as takes an audio_io
- change demo project to use samples 
- random_filename
- slicing needs to take start and end points
  - accept AudioSegment not wav
- s3 banks not creating zip_buffer in a zip- compatible manner
- convert banks zip_file to zip_buffer
  - remove zipfile_to_bytesio utility
- slices -> wav to zipfile
- centre module grid in view
- fork sunvox-dll-python
- load banks from s3
- assert banks
- dump bank fixture to s3
- create bank fixture
- test bank utils
- refactor export
- test export
- add banks default arg
- add protection to model if mod not found
- unique colour choice
- capture tidal demo
- move pool and bank into sampler
- move bank loader into scripts
- move export into utils
- simple (non- optimised) layout grid
- remove offsets
- google colours
- initialise colours on per module basis
- pass colours to module initialisation
- pass colours to pattern initialisation
- mutate colours after every 4th block 
- better nomenclature for tracks vs trigs
- abstract trigs as trig list
- blank doesn't need len(tracks)
- remove model temp code
- should probably be renamed as filter trigs 
- returns an ordered dict as modules is ordered
- add a second patch to demo for testing 
- modify demo to use new bank loader
- move init bank function into banks
- single slot and multi slot sampler
- single slot raises exception if more than one sample
- remove "import RVXXX" nomenclature
- try just importing rv everywhere
- capture controller value too large
- remove velocity check
- move demos out of sv
- local tests or demos
- (string) hex value support 
  - module default values
- note value check for bad int
- get_wav_file check for bad ref
- move banks and sampler pool into project
