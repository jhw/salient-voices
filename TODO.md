### short

### medium

- module valuation to ensure unique module names 
- ensure modules are sorted
- reverse sort modules as by convention output is zero but one tends to define the other way
- move bank stuff into sampler
- FX trig could have a vector classmethod
- equally note trig could have a chord classmethod 
- part of export stems should be moved to sv
- maybe the slicing and zipping bit 
- you could have a zipslice function which took an in memory wav file and a series of keys, and dumped to an in memory zip file
- need unit tests as well as demos 
- need a utility which creates a bank from a zipfile
- need a utility which slices a file and creates a bank from a zipfile
- need a utility which creates a bank from a series of wav files 
- feels like this stuff should live in sv/scripts/banks 
- simple (non- optimised) layout grid

- freeze wash
- jsonschema module validation
- remove RV nomenclature from export.py
- single slot sampler to take repitch arg

### thoughts

- track labelling?
- what's the scaling for filter Resonance default controller value?

### done

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
