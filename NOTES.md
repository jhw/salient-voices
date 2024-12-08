### machine quantisation 08/12/24

- you can probably move the "base" quantisation in here but not the "relative mod" quantisation
- should be able to move base quantisation in there and pass 0, 2, 4 etc (in case of tbp = 2) and not 0, 1, 2, 3, 4 etc
- but mod quantisation is relative to this; you want the 4 to become 8 when tbp = 2 for example
- so the 4 needs to be hardcoded at the generator level, still

---

- what you probably don't want to do is be tempted to split out echo as a separate machine
- it's not an machine in itself, it's an effect; part of something that makes the sound, but not sufficient on its own
- if you split it out you are back in modular space which is what you want to avoid
- in particular because you then have the problem of linking modules together, the link stuff currently being nicely embedded within the machine space

---

- get it to work with berlin and then you are probably done

### decompiler notes 17/11/24

- seem to be patterns with no notes in caravan, space trip
- timeline patterns seem to be switched

```
  File "/Users/jhw/work/salient_voices/env/lib/python3.10/site-packages/rv/modules/sampler.py", line 142, in chunks
    data += pack("<HH", x, y)
struct.error: ushort format requires 0 <= number <= (32767 *2 +1)
```

### slide to 16/08/24

- instead of thinking how to how to join two notes with a slide, you might be better off thinking about adding slide stuff inside an existing note block
- this would seem to simplify things a lot
- you don't need the sustained variable at the baseline level
- you don't need to do either/or for adsr or slide
- you just have to define some extra notes inside the existing block, with slide to fx values
- this makes it pretty easy to do trills and stuff 
- but how can a (random?) trill be parameterised?

--- 

- pass a list of notes with offset, lenth fields
- there should be shorthand for this

### built- in FX 15/08/24

- built in fx are always part of the note column
- slide to must be adjacent to note
- bend is under note
- in many ways they are like mod trigs where you can have multiple in a vector underneath the original

---

- note needs to contain effect and value
- note need not have a module or a note, it can just sit underneath an existing note
- so its a question of the key structure here
- because it has to be rendered in the same column, as they are bound to notes

### chromatic sample distributon 13/08/24

- the chromatic sampler mid points are not working
- because the underlying chromatic sample distribution across the keyboard is not working
- samples are basically being distributed  the same as in the slot sampler (unsurprising)
- ie that the first two slots get filled with samples[:2] and then the sampler fills the remaining slots with chromatic versions of samples[0]
- so you need to be more explicit about sample slot population
- *every* slot must be filled in the chromatic sampler case
- fill the first half of the slots with sample 0, the second half with slot 1 etc
- then you will have to implement a custom repitching strategy for each block
- you can't rely on the default chromatic implementation
- the +1 semitone issue can probably be fixed in here somewhere also

### fills 13/08/24

- change seeds
- increase density
- increase pico pattern length
