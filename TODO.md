### short [01-new-pool-model]

- samples should be inserted into pool as SVSample instances
  - remove recasting in banks code
- add check for type in banks spawn_pool test

- test pool.tags
- test pool.filter_by_tags

### medium

- add Tidal euclid patterns
- add wol vca groove code

- 303 generator demo
- refactor tests and demos to use new generator classes

- sample should carry offset info (not single shot sampler)
- sv project player
- fx trig vector classmethod

### long

- moto upgrade

### thoughts

- remove iteration from single slot sampler? 
  - just makes things less clear; don'r want to hardcode zero index
- project and model pool logic should be moved to pool?
 - seemingly makes things harder
- export test should use wavfile to validate output properties?
  - probably not worth it
- colour mutation?
  - not worth it
- algo to increase colour brightness?
  - not worth as tends to wash out colours
- tidal syntax?
  - not clear you need it, if it's really a performance thing
- track labelling?
  - no point now you have colours
- what's the scaling for filter Resonance default controller value?

### done

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
