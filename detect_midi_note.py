import numpy as np
import wave
import struct
import os
from scipy.fft import fft
import json

def frequency_to_midi(frequency):
    """
    Convert a frequency to its nearest MIDI note number.
    """
    if frequency <= 0:
        return None
    A4 = 440
    midi_number = 69 + 12 * np.log2(frequency / A4)
    return int(round(midi_number))

def detect_midi_note(file_path, start_time, duration):
    """
    Detects the MIDI note number in a WAV file at a specific time.
    
    Args:
    file_path (str): Path to the WAV file.
    start_time (float): Time to start analysis (in seconds).
    duration (float): Duration of the sample to analyze (in seconds).
    
    Returns:
    int: The detected MIDI note number.
    """
    print(f"file_path: {file_path}, start_time => {start_time}, duration => {duration}")
    with wave.open(file_path, 'r') as wav_file:
        # Extract parameters
        frame_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        samp_width = wav_file.getsampwidth()

        # Calculate the number of frames to read
        start_frame = int(frame_rate * start_time)
        num_frames = int(frame_rate * duration)

        # Set position and read frames
        wav_file.setpos(start_frame)
        frames = wav_file.readframes(num_frames)

        # Convert frames to numpy array
        if samp_width == 1: 
            fmt = "%iB" % num_frames * num_channels
        elif samp_width == 2:
            fmt = "%ih" % num_frames * num_channels
        else:
            raise ValueError("Unsupported sample width")

        signal = np.array(struct.unpack_from(fmt, frames))

        # If stereo, take only one channel
        if num_channels == 2:
            signal = signal[0::2]

        # Apply FFT and get frequency
        fft_spectrum = fft(signal)
        freqs = np.fft.fftfreq(len(fft_spectrum))
        index = np.argmax(np.abs(fft_spectrum))
        peak_freq = abs(freqs[index] * frame_rate)

        return frequency_to_midi(peak_freq)

# Example usage
directory = 'F:\\seratoprojects\\stepping_through_stems_pre\\reduced_stems\\'  # Folder containing audio files

# Iterate through each file in the directory
tracks = []
for filename in os.listdir(directory):
    if filename.endswith(".wav"):
        json_file_path = filename.split(".wav")[0]
        # Path to your JSON file
        file_path = os.path.join(directory,f"{json_file_path}.json")
        notes = []
        track = {
            "name": json_file_path,
            "notes": notes
        }
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            onsets = json_data["onsets"]
            offsets = json_data["offsets"]
            file_path = filename  # Replace with your WAV file path
            for i in range(len(onsets)):
                start_time = onsets[i]  # Time to start analysis in seconds
                duration = offsets[i]  # Duration of the sample in seconds
                try:
                    midi_note = detect_midi_note(os.path.join(directory, filename), start_time, duration)
                    if midi_note == None:
                        midi_note = 1
                    elif midi_note < 0:
                        midi_note = 2
                    notes.append({
                        "midi": midi_note,
                        "duration": duration,
                        "time": start_time
                    })
                    print("Detected MIDI Note Number:", midi_note)
                except:
                    pass
        if len(track["notes"]) > 0:
            tracks.append(track)
# Writing the object to a JSON file
with open(os.path.join(directory, "track_data.json"), 'w') as file:
    json.dump({"tracks": tracks}, file, indent=4)
# Detect MIDI note
# midi_note = detect_midi_note(file_path, start_time, duration)
# print("Detected MIDI Note Number:", midi_note)

# Note: The 'detect_midi_note' function is ready to use. Replace 'example.wav' with your actual WAV file path.
# The WAV file needs to be present in the environment where this script is run.
