### short

- simplify colours to one per track
- colour modules same as track
- ensure that every module has a pattern line
- simple (non- optimised) layout grid

### medium

- jsonschema module validation
- remove RV nomenclature from export.py
- single slot sampler to take repitch arg

### thoughts

- track labelling?
- what's the scaling for filter Resonance default controller value?

### done

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
