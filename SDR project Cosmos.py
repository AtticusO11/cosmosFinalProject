from rtlsdr import RtlSdr
import matplotlib.pyplot as plt

# Initialize the SDR
sdr = RtlSdr()

# SDR Configuration
sdr.sample_rate = 2.048e6       # Hz
sdr.center_freq = 100e6         # Hz
sdr.gain = 0
T =  0    
Fs=sdr.sample_rate              
# Automatic gain

# Read samples
num_samples = int(sdr.sample_rate)  # 1 second of data
samples = sdr.read_samples(num_samples)

# Close the SDR connection
sdr.close()

# Display a sample of the data
print(samples[200:210])

# Plot power spectral density
plt.figure()
plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate / 1e6, Fc=sdr.center_freq / 1e6)
plt.xlabel("Frequency (MHz)")
plt.ylabel("Relative power (dB)")
plt.title("Power Spectral Density")
plt.grid(True)

# Free memory
del samples
plt.show()



