```
env) jhw@Justins-Air salient_voices % python dev/decompiler.py ~/packages/sunvox-2-1/examples/NightRadio\ -\ Mechanical\ Heart.sunvox 
INFO: Upgrading Sampler to infinite envelope format
INFO: Upgrading Sampler to infinite envelope format
Traceback (most recent call last):
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 235, in <module>
    chains = ModuleChain.parse_modules(project)
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 38, in parse_modules
    return dfs(0)
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 35, in dfs
    for chain in dfs(prev_index):
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 35, in dfs
    for chain in dfs(prev_index):
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 35, in dfs
    for chain in dfs(prev_index):
  [Previous line repeated 3 more times]
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 30, in dfs
    current_module = module_dict[current_index]
KeyError: -1
```

```
env) jhw@Justins-Air salient_voices % python dev/decompiler.py ~/packages/sunvox-2-1/examples/NightRadio\ -\ Ether\ Winds.sunvox
Traceback (most recent call last):
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 235, in <module>
    chains = ModuleChain.parse_modules(project)
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 23, in parse_modules
    modules = [{"name": mod.name,
  File "/Users/jhw/work/salient_voices/dev/decompiler.py", line 23, in <listcomp>
    modules = [{"name": mod.name,
AttributeError: 'NoneType' object has no attribute 'name'
```

```
(env) jhw@Justins-Air salient_voices % python dev/decompiler.py ~/packages/sunvox-2-1/examples/NightRadio\ -\ Pixel\ Cave.sunvox 
INFO: gen-02-vib-0B-ech-01-dis-06-com-0A-eq-0C-out-00
ERROR: Cannot attach base Module instance.
```
