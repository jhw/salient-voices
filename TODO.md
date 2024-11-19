### short

- add sampler_mod property to SampleTrig and use in sampler population

- do you need trig cloning?

- rename nine09 as Detroit
- replace container test with Detroit instrument test

### medium


- add back 303 as Berlin instrument 
- Berlin instrument 

- simplify demos in favour of tests
  - tests should dump sunvox files
  
- check for %s
- check/test rv instruments

- rename note as relative_note


### thoughts

- model tests?
  - still can't see the need

### gists 

- reverse/retrig

- freezing
- polly vocals/ vocoder
- 303 slide
- pico play modes
- resampling

- granular
- sv drum
- kicker

### long

- moto upgrade

### thoughts

- layout management for decompiler?
  - belies the bare bones nature

### done

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

