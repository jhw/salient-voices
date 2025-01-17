import os
import sys
import zipfile
from pathlib import Path

def process_zip(input_zip_path):
    # Ensure the input path is valid
    if not Path(input_zip_path).is_file():
        print(f"Error: File not found at {input_zip_path}")
        return

    # Load the input zip file into memory
    with zipfile.ZipFile(input_zip_path, 'r') as input_zip:
        # Check if meta.json is present
        if 'meta.json' not in input_zip.namelist():
            print("Error: meta.json not found in the zip file.")
            return

        # Ensure the tmp directory exists
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)

        # Path for the output zip file
        output_zip_path = tmp_dir / "sample-archive.zip"

        # Create a new zip file in memory
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as output_zip:
            # Copy meta.json to the new zip file
            meta_data = input_zip.read('meta.json')
            output_zip.writestr('meta.json', meta_data)

            # Find the required audio file
            audio_file = next((
                name for name in input_zip.namelist()
                if name.endswith(".wav") and "-pat-" in name
            ), None)

            if audio_file:
                # Copy the audio file and rename it to audio/raw.wav
                audio_data = input_zip.read(audio_file)
                output_zip.writestr('audio/raw.wav', audio_data)
            else:
                print("Error: No matching .wav file found in the zip file.")
                return

    print(f"Processed zip file saved to {output_zip_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_zip>")
        sys.exit(1)

    input_zip_path = sys.argv[1]
    process_zip(input_zip_path)
