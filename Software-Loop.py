import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def digital_modulation(bits):
    return 2 * bits.astype(np.float32) - 1

def digital_demodulation(symbols):
    return (symbols > 0).astype(np.uint8)

# Load RGB image
img = Image.open("Teachers/Lev_Tauz.jpg").convert("RGB")
img_array_rgb = np.array(img)
original_shape = img_array_rgb.shape  # (H, W, 3)

channels = []
received_channels = []

chunk_size = 8000  # bits per chunk

for c in range(3):
    # Extract channel and flatten
    channel = img_array_rgb[:, :, c]
    flat_channel = channel.flatten().astype(np.uint8)
    
    # Convert to bits
    bits = np.unpackbits(flat_channel, bitorder='big')
    
    # Modulate bits
    symbols = digital_modulation(bits)
    
    received_symbols = []
    # Simulate transmission chunk-wise
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i + chunk_size]
        rx_chunk = chunk.copy()  # perfect channel
        received_symbols.append(rx_chunk)
    
    received_symbols = np.concatenate(received_symbols)
    
    # Demodulate bits
    received_bits = digital_demodulation(received_symbols)
    received_bits = received_bits[:len(bits)]
    
    # Pack bits back to bytes
    received_bytes = np.packbits(received_bits, bitorder='big')
    
    # Reshape back to channel shape
    received_channel = received_bytes.reshape(channel.shape)
    received_channels.append(received_channel)

# Stack channels back into RGB image
received_rgb_array = np.stack(received_channels, axis=2)

# Plot original and received
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.title("Original Image (RGB)")
plt.imshow(img_array_rgb)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Received Image (RGB)")
plt.imshow(received_rgb_array)
plt.axis("off")

plt.tight_layout()
plt.show()
