import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Load the audio recording using a library such as librosa
import librosa

audio, sr = librosa.load("audio_recording.wav")

# Perform a Fourier transform to extract the frequency information
fourier = np.abs(np.fft.fft(audio))
frequencies = np.fft.fftfreq(len(audio), 1/sr)

# Find the peaks in the frequency domain
peaks, _ = find_peaks(fourier, distance=sr//10)

# Filter out the peaks that are not related to the RPM signal
filtered_peaks = [p for p in peaks if np.abs(frequencies[p]) > 500 and np.abs(frequencies[p]) < 1000]

# Plot the filtered peaks to verify the results
plt.plot(frequencies[filtered_peaks], fourier[filtered_peaks], "x")
plt.show()
