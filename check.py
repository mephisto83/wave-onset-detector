import aubio
import numpy as np

# Open the audio file
filename = 'PRICEY_LEAD_110BPM_DMAJOR.wav'  # Replace with your audio file path
samplerate = 0  # Use 0 to use the original samplerate of the file
win_s = 512  # FFT size (window size)
hop_s = win_s // 2  # Hop size

s = aubio.source(filename, samplerate, hop_s)
samplerate = s.samplerate

# Create an onset detection object
onset = aubio.onset("default", win_s, hop_s, samplerate)

# List to store onsets
onsets = []

# Process the audio file
while True:
    samples, read = s()
    if onset(samples):
        print("%f" % onset.get_last_s())
        onsets.append(onset.get_last_s())
    if read < hop_s:
        break

# Convert onset times from samples to seconds
onsets_in_seconds = onsets
print("Onsets in seconds:", onsets_in_seconds)
