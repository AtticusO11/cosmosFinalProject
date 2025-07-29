from adi import Pluto
import matplotlib.pyplot as plt
import numpy as np

# Initialize PlutoSDR
sdr = Pluto("usb:0.9.5")
sdr.sample_rate = int(2.048e6)
sample_rate = sdr.sample_rate
sdr.rx_lo = int(435e6)
center_freq = sdr.rx_lo
sdr.rx_rf_bandwidth = int(2e6)  # Optional: Bandwidth matching sample rate
sdr.rx_buffer_size = 4096       # Number of complex samples to read

# Read samples
samples = sdr.rx()

# Print a slice of the samples
print(samples[200:210])

# Plot power spectral density
plt.psd(samples, NFFT=1024, Fs=sample_rate/1e6, Fc=center_freq/1e6)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.title("PlutoSDR PSD")
plt.grid(True)
plt.show()

