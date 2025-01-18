### short [01-slide-to]

- extend sample length on initialisation
- pico waveforms
- reduce blank probability between notes?
- wol scales

### medium

### demos

- slide up/down
- euclid09 cutoff 
- reverse/retrig
- city dreams bass
- polly
- vocoder
- vocal chords

### gists

- samplebrain
- vocoder

### pending

- sunvox 2.0 file format
- rv circular imports

### thoughts

- avoid container.modules flattening modules?
  - but how? renaming?

### done

- refactor slide-to handling
- still getting some notes rendered in last step
- how to set fx pattern?
- check trig constructor passing
- purge fx support
- berlin distortion
- remove bpm component from euclid/resampler echo delay
- recover slide demos into dev
- randomise ADSR sound parameters
- refactor BerlinSampleTrig as MultiSynthSampleTrig
- vitling scales
- pass scale as env variable
- perkons groove
- include index in last variable
- move SVNoteOff trig to trigs
- randomise wave
- include wave in berlin sound
- refactor note as pitch
- purge SVMachineTrigs from berlin demo
- purge SVMachineTrigs from resampler demo
- purge SVMachineTrigs from euclid demo
- sampler doesn't seem to have any sound
- multiple patches with different sounds
- complete machine, track configuration
- BerlinSampleTrig to extend SVSampleTrig
- NOTE_OFF
- rename SimpleBank as SimpleZipBank
- check why euclid doesn't seem to be calling container.render
- add back chatgpt script to initialise archive 
- change bank so it doesnt extend simple bank but is its own version
- initialise from zip but extend dict and keep stuff in memory.
- new init slices method to initialise slices as in memory items 
- create a merge branch for main + 01-berlin03-demo
- spawn blank patches after each for wash
- rename namespace as kick
- add filter function looking for BD in sample name
- add iterator block -> namespace, sample filter, density, temperature
- add new tracks for snare and hats 

