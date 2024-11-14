### short [01-decompiler]

- link modules
- save project

### medium

- filter out empty tracks
- layout management
- export controller properties to yaml

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

### done

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

