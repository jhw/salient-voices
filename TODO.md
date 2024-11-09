### short

- re- simplify 909 demo?

### medium

- digitakt II dual euclidian

### sv

### thoughts

- model.py tests?
  - not sure it's worth it, given they are covered in other places

### gists 

- pico glitch samples

- decompiler
- freezing
- polly vocals
- resampling
- 303 w/ slides

- sample likeness clustering
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

