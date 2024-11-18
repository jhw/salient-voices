### short [01-poly-chromatic-demo]

- add notes re sampler structure
- check sampler uses str(sample) as slot key identifier
- ask chatgpt to refactor sv sample to include querystring with note, default value 0 
- sample trig (and others?) to include note as part of sample reference

### medium

- refactor sampler note as relative note
- add back container test

### thoughts

- model tests?
  - still can't see the need

### gists 

- pico glitch samples

- freezing
- polly vocals + sv vocoder
- resampling
- 303 slide

- granular
- sv drum
- kicker
- city dreams bass

### long

- moto upgrade

### thoughts

- layout management for decompiler?
  - belies the bare bones nature

### done

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

