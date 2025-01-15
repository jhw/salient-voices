### short 

- berlin03/mikey303 demo

### medium

- berlin03 slide

- freeze demo
- city dreams bass demo
- vocoder demo
- polly demo

### pending

- sunvox 2.0 file format
- rv circular imports

### thoughts

### thoughts

- resampler to do slicing on bank init?
  - can't be bothered
  - if you include the raw file in the zip then the zip file will still be the same size
  - it's not worth hacking this just so you can quantise; it's only intended as a demo
- why does berlin density 1.0 leaves gaps?
  -  because of quantisation; terms don't always fill them
- force final end note in berlin demo?
  - not worth it; extra complexity for no change in sound
- refactor main detroit test to use tpb?
  - it's really not worth it until you want to mix (eg) bass with beats, which is something for the downstream client level to handle
  - maybe euclid v1-1 which can handle bass 
  - for now berlin acts as a good example
- implement metamodules?
  - simply not worth it as you need to encode note generating behaviour, when metamodules are just simple wrappers  
- refactor project render_blank()?
  - not worth it
- rename note as relative_note?
  - is fine as is

### done

- per track sample selection
- track addition
- check archive is a zip file
- default sampler pitch, cutoff variables
- random_pattern, random_groove
- remove beats api
- check pydub installed
- comment out local bank functionality
- move sv bank into tests and rename
- target wav file
- script taking options for file, slices, samples
- slice with AudioSegment
- dump slices output
- remove machines directory
- remove algos
- check if you still need pico-default.zip for tests
- remove beats and machines
- add beats API pitch 
- add cutoff state fields and operators 
- add to dict / json / base64 serialisation 
- save to local files
- load from local files
- save to local zip
- load from local zip
- check join doesn't duplicate keys
- move SVPool into sampler
- sampler to apply cutoff
- remove is_online
- add urlparse
- refactor detroit api to use sound, pitch, cutoff
- add note self.cutoff
- refactor defaults application
- try removing self.note
- add note self.pitch and refactor note as pitch
- convert sample string to use querystring
- check mod_sampler removed
- clean up trigs
- move note into sv trig base
- merge samplers
- check index_of indexes into list
- project pool creation to append note
- sampler to split sample into sample and note
- sampler to adjust relative note
- pass trig to index of 
- add bank join() function
- pool definitions to use spawn_pool()
- convert pool to set
- remove sample
- remove detroit sound
- remove bank name
- remove querystring
- remove note
- rename tests
- remove berlin
- remove pydub
- remove start and cutoff
- simplify sampler cutoff/trimming
- don't like bank = None declaration
- pass matching function to spawn pool
- detroit test to use matcher for different tracks
- refactor TEMP
- add bank fn to spawn pool
- move pool back into bank
- remove mod/fx stuff
- rename banks as bank, sounds as sample
- remove sample tag
- replace banks with bank
- test for get wav
- add get_wav to bank

```
ERROR: test_detroit_machine (tests.machines.beats.detroit.DetroitMachineTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/jhw/work/salient_voices/tests/machines/beats/detroit.py", line 127, in test_detroit_machine
    add_track(container = container,
  File "/Users/jhw/work/salient_voices/tests/machines/beats/detroit.py", line 95, in add_track
    machine.render(generator = Beat,
  File "/Users/jhw/work/salient_voices/sv/machines/__init__.py", line 33, in render
    for i, trig_block in generator(self,
  File "/Users/jhw/work/salient_voices/tests/machines/beats/detroit.py", line 27, in Beat
    trig_block = self.note(volume = volume)
  File "/Users/jhw/work/salient_voices/sv/machines/beats/detroit.py", line 56, in note
    sample = self.sound.clone()
  File "/Users/jhw/work/salient_voices/sv/machines/beats/__init__.py", line 24, in sound
    return self.sounds[self.sound_index]
IndexError: list index out of range
```

- remove s3 stuff
- why is sample.as_dict() required if you have __get|setstate__?
- harmonise berlin to/from dict/json methods with detroit
- remove detroit reverb and distortion
- SVSample shouldn't need to extend dict
- detroit sound
- berlin sound serialisation
- beats api
- test sampler fx 
- sunvox 2-0 file format [notes]
- reply to matthew
- refactor berlin test so only a single resonance is selected each time
- berlin slide up/down skeleton
- refactor trig.increment as trig.set_position
- test DrumSynth mute
- add resonance options to berlin test random_sound
- test initial filter resonance parameterisation
- implement wave parameter as enum
- pass wave parameter to berlin
- refactor machine/__init__.py as machine.py
- remove load_yaml
- abstract echo modulation
- base class implementing sound api for berlin, detroit
- berlin test generator to switch sounds like detroit
- berlin test main script to initialise sounds and pass to machine
- abstract generator sound randomisation into randomise_sounds function
- check handling of sustain term parameter
- add sound api to berlin class
- new berlin sound class
  - attrs for whatever is currently being passed to note
- add tbp_adjusted_xxx values in container
- check detroit with tbp = 2
- berlin is only producing notes in second half
- reduce n_ticks to 16 in each case
- remove fx demo
- try removing default bpm and n_ticks args from Container constructor
- pass tpb as container arg
- consider if n_ticks arg in machine tests needs to be quantised for tbp
- adjust all ghost echos in machines tests to use tpb
- adjust all euclid refs in machines tests to use tpb
- adjust all perkons refs in machines tests to use tpb
- refactor berlin to adjust perkons `tpb` as part of wrapper
- implement sampler cutoff trimming
- implement sampler start trimming
- add default cutoff 16 seconds
- don't pass bpm to sampler
- remove sampler cutoff variable 
- add value error during setters
- tests for rendering and start/cutoff
- checks for start > cutoff and fx without cutoff
- don't render sample note/fx to json if 0/null values
- and start and cutoff fields to sample 
- add default 32 length
- add back snare
- refactor samples, notes as sounds
- refactor sample_cutoff as sound_cutoff
- how to get notes the full range of base notes
- move detroit into tests/__init__.py
- remove sample/pool/bank stuff from test
- test to initialise tokyo classes
- remove sample stuff from module
- add subclassing
- copy detroit including tests
- undo **kwargs passed to instrument constructors
- rename SVTrigGroup as SVMachineTrigs
- tests to initialise modules with random colours
- pass colours down from machine subclass constructors
- render bg_color in project module rendering
- pass colour to sv machine constructor
- include colour in sv machine render
- define colours at machine level
- pass colours down from demo level
- remove project custom layout code
- update polly gist
- simplify berlin variable names
- wrap decompiler sampler error
- report decompiler fmx error
- pass perkons as env variable
- 303 basic note
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

