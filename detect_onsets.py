import aubio
import numpy as np
import os
import json

# Set the directory containing the audio files
directory = 'F:\\seratoprojects\\stepping_through_stems_pre\\reduced_stems\\'  # Folder containing audio files
def detect_offsets(file_path, onsets, samplerate, threshold=0.01, min_silence_duration=0.1):
    """
    Detects offsets in the audio file given the onsets.
    """
    win_s = 512
    hop_s = win_s // 2
    s = aubio.source(file_path, samplerate, hop_s)
    offsets = []
    buffer_size = int(min_silence_duration * samplerate // hop_s)  # Buffer size for silence duration

    for onset in onsets:
        s.seek(int(onset * samplerate))
        silence_buffer = []

        while True:
            samples, read = s()
            rms = np.sqrt(np.mean(np.square(samples)))
            silence_buffer.append(rms < threshold)

            if len(silence_buffer) > buffer_size and all(silence_buffer[-buffer_size:]):
                # Correcting this line to use 'read' instead of 's.read_samples'
                offsets.append(s.hop_size * read / samplerate)
                break

            if read < hop_s:
                # Also correcting this line
                offsets.append(s.hop_size * read / samplerate)
                break

    return offsets

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

        # Detect offsets
        offsets_in_seconds = detect_offsets(file_path, onsets_in_seconds, samplerate)

        # Write the onset and offset data to a JSON file
        json_filename = filename.replace('.wav', '.json')
        json_path = os.path.join(directory, json_filename)
        with open(json_path, 'w') as json_file:
            json.dump({'onsets': onsets_in_seconds, 'offsets': offsets_in_seconds}, json_file)

        print(f"Processed {filename}, onsets and offsets saved to {json_filename}")
