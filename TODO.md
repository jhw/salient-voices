### short

- refactor main detroit test to use bpm
- 303 basic note
- synchronise mod and pattern colours
- test for name rendering

### medium

- update polly gist
- 303 slide_up/down, slide_to, trill notes
- add start variable to sample
- SV drum machine / tokyo
- berlin test clustering and trilling
- detroit resampler demo

### thoughts

### gists 

- stutter
- freezing
- polly vocals/vocoder
- autotune
- 303 slide
- pico play modes
- granular
- kicker

### long

- moto upgrade

### thoughts

- refactor project render_blank()?
  - not worth it
- rename note as relative_note?
  - is fine as is

### done

- reply to matthew
- fix polly demo
- test project layout
- berlin demo to pass explicit delay parameter
- berlin demo to accept scaling arg
- make berlin demo sparser and add more echo
- simplify Berlin demo as single note with minimal sustain options
- add groove to Detroit FX demo
- matthew reply
- machine tests
- add fade out when trimming
- shred lagrange point
- global sample cutoff
- replace sampler sz variable with self cutoff 
- add skeleton code to sampler to trim all samples
- implement sample trimming
- move cutoff default value from sv sampler machine base to Detroit class 
- increased default cutoff value and added detroit default cutoff of 0.5
- pass cutoff from machine base to sampler along with root
- add cutoff partner to sv sampler machine base with default value 1
- machine to use SVModule
- subclass SV machine base for sampler 
- remove machine group base classes
- test for mechanical heart sampler error
- decompiler is reversing modules
- decompiler to ask for directory
- add beats interface with xxx_sound nomenclature (not xxx_sample)
- look old detroit test
- modify for fx
- nest detroit tests
- implement rev, ret2, ret4
- with_audio_segment decorator
- add skeleton for performing pydub operation
- get_wav needs to return io.BytesIO
- separate sample and sampler
- add mod support to svsamplenote
- pass bpm, tpb to sampler
- install pydub
- pass arg to test.py
- rename instruments as patches
- introduce patch sub directoriees for beats, bass
- adding a second track to detroit demo results in it being appended!
- instrument tests fail when run individually
- add sample toggling
- replace berlin reference with machine
- dynamic perkons lookup
- add pattern densities
- abstract track code
- add perkons.humanise
- shuffle samples at main level
- add multiple grooves
- add extra samples 
- add pool
- add random pattern
- detroit euclid
- detroit perkons
- bad controller values with 3 digits pass silently 
- review exceptions
- rename model as trigs
- try merging trig classes again
- check for %s
- unify trig classes
- detroit test echo s&h
- why do instruments tests require this seed parameter?
- should berlin instrument embed mikey303 samples? (probably)
- add back 303 as berlin instrument 
- berlin instrument test
- retire demos/euclid09
- detroit test to dump output
- replace container test with Detroit instrument test
- rename nine09 as Detroit
- remove trig cloning
- move MultiSynthSampleTrig into core model
- add notes to MultiSynthSampleTrig
- change is_sampler to see if class extends rv sampler
- add SVModule.is_sampler property
- rename sample_mod as sampler_mod
- rename SlotSampleTrig as simply SampleTrig
- indirect sample trig to extend sample trig 
- rename chromatic sample trig as indirect sample trig 
- move chromatic sample trig into instrument
- test polly slot demo
- test polly chromatic demo
- add back sampler test
- add back container test
- blank querystring if empty
- fix negative note handling
- refactor sv sample so note is an argument and querystring is a property
- refactor 303 note handling to clone sample and add note
- check 303 demo
- add note to cloned sample
- clone base sample at 909 level
- add sample ref clone 
- sampler to adjust relative note based on sample note 
- sample tests
- add querystring and note support to sample ref
- fix randomise tags problem
- fix 303 sampler problem 

- consider SVSample as dict to avoid euclid09 demo leading to 
- try and remove cast_sample
- euclid cli failing to serialise/deserialise samples
- refactor sample ref as object
- move sample ref to sampler
- add note to sample re mods attachment point
- add notes re sampler structure
- rationalise base and slot samplers, moving note_samples stuff into slot sampler
- move chromatic sampler into 303 demos as single shot sampler
- move chromatic sample trig into 303 demo
- re- test demos
- test two samples
- add local chromatic sampler
- use single sample
- rename nine09 as three09
- remove echo
- copy slot demo to chromatic demo
- move 909 definition inline
- resize modules
- decompiler module layout management
- replace root note with relative note
- fix sample pitching
- nine09 needs ability to set sample index directly
  - increment/decrement
- container render should have default seeds arg
- instruments should have default volume 1
- when container writes project, don't assume the existence of an instrument

- controller yaml export
- max chains
- remove dots and spaces from short names

```
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 76, in <dictcomp>
    modules = {mod.index: mod for mod in project.modules}
AttributeError: 'NoneType' object has no attribute 'index'
```

```
 File "/Users/jhw/work/salient_voices/env/lib/python3.10/site-packages/rv/project.py", line 80, in attach_module
    raise RuntimeError("Cannot attach base Module instance.")
RuntimeError: Cannot attach base Module instance.
```

```
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 24, in <listcomp>
    modules = [{"name": mod.name,
AttributeError: 'NoneType' object has no attribute 'name'
```

```
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 31, in dfs
    current_module = module_dict[current_index]
KeyError: -1
```

- pass a directory not a filename 
- capture exceptions gracefully
- only render unique patterns
- don't render blanks eg Elochka gen-0D-ech-02-fla-0F
- add notes without modules and note off
- save project
- create pattern with data
- filter out empty tracks
- flatten tracks
- link modules
- use real project name and create slug for output
- set note module indexes
- problem with Base module
- attach modules to project
- create project
- clone pattern, rejecting unwanted notes
- convert pattern groups to a list
- filter_mod_chains to validate out/0 and also remove it
- move filter_mod_chains, parse_timeline into classes as static methods
- update sample909 demo
- init_colours should take a list of mod names
- per- phrase colours
- pool tag_mapping arg should be renamed tag_patterns
- init_banks needs to create tmp
- replace parse with local version
- rename randomiser methods as per below
- update to use fixtures zip only
- copy gist as 909 demo
- cli/parse
- check use of SVNoteTrig.value
- notefn volume helpers
- when dry_level = 0, vel is not returned as part of SVSlotSampleNote note_kwargs, which means vel uses a default value of 0, which returns a null arg
- trig.vel max(1) condition appears to be being bypassed during rendering
- remove ability to pass note arg to Nine09.note()
- separate SVSampleTrig class
- flatten demos structure

