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
