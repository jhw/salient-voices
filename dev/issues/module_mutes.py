import os

import rv.api
from rv.api import Project
from rv.modules.drumsynth import DrumSynth
from rv.modules.analoggenerator import AnalogGenerator

# Create a new SunVox project
project = Project()

# Add modules
analog_generator = project.new_module(AnalogGenerator, name="AG")
drum_synth = project.new_module(DrumSynth, name="DS")

# Connect the modules using the project.connect method
project.connect(analog_generator, project.output) 
project.connect(drum_synth, project.output) 

# Ensure the tmp directory exists
output_dir = "tmp"
os.makedirs(output_dir, exist_ok=True)

# Save the project to the specified file
filename = os.path.join(output_dir, "module-mute-test.sunvox")
with open(filename, "wb") as f:
    project.write_to(f)

print(f"Project saved to {filename}")
