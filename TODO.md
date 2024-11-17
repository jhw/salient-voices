### short

- instruments should have default volume 1
- container render should have default seeds arg
- nine09 needs ability to set sample index directly
  - increment/decrement

### medium

- why is pitch messed up?
- decompiler module layout management

### thoughts

- replace sys.args stuff with argsparse?
  - not worth it
- model tests?
  - still can't see the need

### decompiler

- patterns with no notes in caravan, space trip
- timeline patterns seem to be switched

```
  File "/Users/jhw/work/salient_voices/env/lib/python3.10/site-packages/rv/modules/sampler.py", line 142, in chunks
    data += pack("<HH", x, y)
struct.error: ushort format requires 0 <= number <= (32767 *2 +1)
```

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

