from pydub import AudioSegment

import io
import zipfile

def slice_wav_equal(wav_io, zip_paths, fade = 3):
    audio_io = AudioSegment.from_file(wav_io, format = "wav")
    return slice_audio_segment_equal(audio_io = audio_io,
                                     zip_paths = zip_paths,
                                     fade = fade)

def slice_audio_segment_equal(audio_io, zip_paths, fade = 3):
    chunk_size = int(len(audio_io) / len(zip_paths))
    zip_items = []
    for i, zip_path in enumerate(zip_paths):
        start_time = i * chunk_size
        end_time = start_time + chunk_size
        zip_item = {"zip_path": zip_path,
                    "start_time": start_time,
                    "end_time": end_time}    
        zip_items.append(zip_item)
    return slice_audio_segment_custom(audio_io = audio_io,
                                      zip_items = zip_items,
                                      fade = fade)

def slice_audio_segment_custom(audio_io, zip_items, fade = 3):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for zip_item in zip_items:
            start_time = zip_item["start_time"]
            end_time = zip_item["end_time"]
            zip_path = zip_item["zip_path"]
            chunk_audio = audio_io[start_time:end_time].fade_in(fade).fade_out(fade)
            chunk_io = io.BytesIO()
            chunk_audio.export(chunk_io, format = "wav")
            chunk_io.seek(0)
            zip_file.writestr(zip_path, chunk_io.read())
    zip_buffer.seek(0) # ensure zipfile.ZipFile can be created from it
    return zip_buffer
    

if __name__ == "__main__":
    pass
