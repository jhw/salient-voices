### short

- unit tests
- s3 banks
- wav to zipfile

### medium

- algo to increase colour brightness

- fx trig vector classmethod
- note trig chord classmethod

- single slot sampler to take repitch arg
- jsonschema module validation
- freeze wash

### thoughts

- tidal syntax?
  - not clear you need it, if it's really a performance thing
- track labelling?
  - no point now you have colours
- what's the scaling for filter Resonance default controller value?

### done

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
