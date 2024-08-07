### short

- single slot and multi slot sampler
- single slot takes repitch arg
- single slot raises exception if more than one sample
- move init bank function into banks
- extend it to take more than one sample ref
- modify demo to use new bank loader

### medium

- remove RVXXX nomenclature from export.py


### thoughts

- what's the scaling for filter Resonance default controller value

### done

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
