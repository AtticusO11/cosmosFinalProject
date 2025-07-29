import numpy as np
import cv2
import matplotlib.pyplot as plt
from adi import Pluto
from reedsolo import RSCodec

# Load grayscale image and flatten to bytes
img = cv2.imread('Teachers/Ethan_Ge.jpg', cv2.IMREAD_GRAYSCALE)
if img is None:
    raise FileNotFoundError("Could not load image at 'Teachers/Ethan_Ge.jpg'")
img_shape = img.shape
img_bytes = img.flatten()

# Simple 4-PAM: map each byte to 4 symbols (2 bits each)
def bytes_to_symbols(data):
    symbols = []
    for b in data:
        symbols.append((b >> 6) & 0b11)
        symbols.append((b >> 4) & 0b11)
        symbols.append((b >> 2) & 0b11)
        symbols.append(b & 0b11)
    return np.array(symbols)
def rs_encode(data_str, nsym=4):
    rs = reedsolo.RSCodec(nsym)
    return rs.encode(bytearray(data_str, 'utf-8'))

def rs_decode(encoded_bytes):
    rs = RSCodec(4)  # Use same nsym as encoding (4)
    # decode returns just the decoded message bytes (may return tuple with 1 element)
    decoded_bytes = rs.decode(encoded_bytes)
    if isinstance(decoded_bytes, tuple):  # sometimes returns (msg,)
        decoded_bytes = decoded_bytes[0]
    return decoded_bytes

symbols = bytes_to_symbols(img_bytes)

# Map 4-PAM symbols {0,1,2,3} to amplitude levels {-3, -1, 1, 3}
pam_levels = np.array([-3, -1, 1, 3])
tx_symbols = pam_levels[symbols]

# Upsample (repeat each symbol 10 times)
upsample_factor = 10
tx_waveform = np.repeat(tx_symbols, upsample_factor)

# Normalize to max amplitude range for PlutoSDR (-1 to 1)
tx_waveform = tx_waveform / np.max(np.abs(tx_waveform))

# Create complex baseband signal (I = waveform, Q = 0)
tx_samples = tx_waveform.astype(np.float32) + 1j * np.zeros_like(tx_waveform)

# Initialize PlutoSDR for TX/RX
sdr = Pluto("usb:0.9.5")
sdr.tx_lo = int(435e6)
sdr.tx_sample_rate = int(2.048e6)
sdr.tx_rf_bandwidth = int(2e6)
sdr.tx_cyclic_buffer = False

sdr.rx_lo = sdr.tx_lo
sdr.rx_sample_rate = sdr.tx_sample_rate
sdr.rx_rf_bandwidth = sdr.tx_rf_bandwidth
sdr.rx_buffer_size = len(tx_samples)

print("Starting transmission...")
sdr.tx(tx_samples)
print("Transmission done.")

print("Starting reception...")
rx_samples = sdr.rx()
print("Reception done.")

# Extract real part (I) as symbols (ignore Q for PAM)
rx_waveform = rx_samples.real

# Downsample by factor 10 (match upsample_factor)
downsample_factor = 10
rx_samples_ds = rx_waveform[::downsample_factor]

# Demap 4-PAM
pam_levels = np.array([-3, -1, 1, 3])
symbols_rx = np.argmin(np.abs(rx_samples_ds[:, None] - pam_levels[None, :]), axis=1)

def symbols_to_bytes(symbols):
    bytes_out = []
    for i in range(0, len(symbols), 4):
        if i+3 >= len(symbols):
            break
        b = (symbols[i] << 6) | (symbols[i+1] << 4) | (symbols[i+2] << 2) | symbols[i+3]
        bytes_out.append(b)
    return np.array(bytes_out, dtype=np.uint8)

received_bytes = symbols_to_bytes(symbols_rx)

# Recover original image
img_recovered = received_bytes[:img_shape[0]*img_shape[1]].reshape(img_shape)

# Show recovered image
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(img, cmap='gray')
plt.title("Original Image")
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(img_recovered, cmap='gray')
plt.title("Recovered Image")
plt.axis('off')

plt.tight_layout()
plt.show()

# Cleanup
sdr.tx_destroy_buffer()
del sdr
