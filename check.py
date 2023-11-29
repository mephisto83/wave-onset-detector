import aubio
import numpy as np
import os
import json

# Set the directory containing the audio files
directory = 'F:\\seratoprojects\\sitting_down_stems\\stems\\'  # Folder containing audio files

# Iterate through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".wav"):
        file_path = os.path.join(directory, filename)

        samplerate = 0  # Use original samplerate
        win_s = 512  # FFT size
        hop_s = win_s // 2  # Hop size

        s = aubio.source(file_path, samplerate, hop_s)
        samplerate = s.samplerate

        onset = aubio.onset("default", win_s, hop_s, samplerate)
        onsets = []

        while True:
            samples, read = s()
            if onset(samples):
                onsets.append(onset.get_last_s())
            if read < hop_s:
                break

        onsets_in_seconds = onsets

        # Write the onset data to a JSON file
        json_filename = filename.replace('.wav', '.json')
        json_path = os.path.join(directory, json_filename)
        with open(json_path, 'w') as json_file:
            json.dump(onsets_in_seconds, json_file)

        print(f"Processed {filename}, onsets saved to {json_filename}")
