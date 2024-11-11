### short

- per- phrase colours
- model tests
- init_banks needs to create tmp
- pool tag_mapping arg should be renamed tag_patterns
- update sample909 demo

### medium

- digitakt II dual euclidian

### thoughts

### gists 

- pico glitch samples

- decompiler
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

