import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm
import time

from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

def digital_modulation(bits):
    return 2 * bits.astype(np.float32) - 1

def digital_demodulation(symbols):
    return (symbols > 0).astype(np.uint8)

# SDR setup
fs = int(10e6)
sps = 1  # Speed over robustness

tx = Pluto("usb:0.4.5")
tx.tx_gain = 90
rx = tx
rx.rx_gain = 90

tx.sample_rate = fs
rx.sample_rate = fs

system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)

# Load and resize image
img = Image.open("knee.jpg").convert("RGB")
img = img.resize((64, 64), Image.Resampling.LANCZOS)
img_array_rgb = np.array(img)
H, W, _ = img_array_rgb.shape

# Combine RGB channels into 1 stream
flat_rgb = img_array_rgb.reshape(-1, 3).flatten()  # Interleaved R, G, B
bits = np.unpackbits(flat_rgb, bitorder='big')
symbols = digital_modulation(bits)

chunk_size = 8000
received_symbols_chunks = []

print("Transmitting combined RGB data...")
start_time = time.time()

for i in tqdm(range(0, len(symbols), chunk_size), desc="Chunks"):
    chunk = symbols[i:i + chunk_size]
    system.transmit_signal(chunk)

    expected_samples = len(chunk) * sps
    received_samples = np.array([], dtype=np.complex64)
    attempts = 0
    max_recv_attempts = 50

    while len(received_samples) < expected_samples and attempts < max_recv_attempts:
        new_samples = system.receive_signal()
        received_samples = np.concatenate((received_samples, new_samples))
        attempts += 1

    if len(received_samples) < expected_samples:
        print(f"Warning: only received {len(received_samples)} samples, expected {expected_samples}")

    rx_chunk = received_samples[sps // 2 :: sps]
    rx_chunk = rx_chunk[:len(chunk)]
    received_symbols_chunks.append(rx_chunk)

print(f"Transmission done in {time.time() - start_time:.2f} sec")

# Reconstruct full RGB array
received_symbols = np.concatenate(received_symbols_chunks)
received_bits = digital_demodulation(received_symbols)
received_bits = received_bits[:len(bits)]  # Trim to original length

received_bytes = np.packbits(received_bits, bitorder='big')
if len(received_bytes) < flat_rgb.size:
    padded = np.zeros(flat_rgb.size, dtype=np.uint8)
    padded[:len(received_bytes)] = received_bytes
    received_bytes = padded
else:
    received_bytes = received_bytes[:flat_rgb.size]

# Reshape into RGB image
received_rgb = received_bytes.reshape(H, W, 3)

# Plot
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(img_array_rgb)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Received Image")
plt.imshow(received_rgb)
plt.axis("off")

plt.tight_layout()
plt.show()
