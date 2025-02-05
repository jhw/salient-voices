### short

- refactor track as sequence

### medium

- new bank to implement variety of simple fx
- use fwd.wav as default sample
- detroit demo to toggle fx not sample
- client/sampler model, track
- improved tests

### pending

- sunvox 2.0 file format
- rv circular imports

### thoughts

- add back resampler?
  - this may be better done at the m8 level

### done

- add getter/setter for rv_samples in sampler
- remove refs to relative note
- check pitch, cutoff refs
- remove sample_string refs in trigs
- remove sample_string refs in sampler
- remove sample qs support and cutoff/pitch support in sampler
- SVSimpleBank doesn't need to extend dict
- remove resampler, slicer bank
- remove berlin, bass packs
- remove detroit09b


