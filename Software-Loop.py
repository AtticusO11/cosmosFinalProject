import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from reedsolo import RSCodec

def digital_modulation(bits):
    return 2 * bits.astype(np.float32) - 1

def digital_demodulation(symbols):
    return (symbols > 0).astype(np.uint8)

def apply_noise(symbols, snr_db=20, burst_prob=0.1, burst_strength=5.0):
    snr_linear = 10 ** (snr_db / 10)
    signal_power = np.mean(symbols**2)
    noise_power = signal_power / snr_linear

    noise = np.random.normal(0, np.sqrt(noise_power), size=symbols.shape)

    bursts = np.random.rand(*symbols.shape) < burst_prob
    noise[bursts] += np.random.normal(0, burst_strength * np.sqrt(noise_power), size=np.count_nonzero(bursts))

    return symbols + noise

# Load image
img = Image.open("knee.jpg").convert("RGB")
img_array_rgb = np.array(img)
original_shape = img_array_rgb.shape  # (H, W, 3)

# Reed-Solomon parameters
rs = RSCodec(20)  # 20 parity bytes
chunk_size_bytes = 235  # max message length with nsym=20 (<=255-nsym)
chunk_size_bits = chunk_size_bytes * 8

received_channels = []
symbol_log = []
received_symbol_log = []

for c in range(3):
    channel = img_array_rgb[:, :, c]
    flat_bytes = channel.flatten().astype(np.uint8)

    # RS encode chunks
    encoded_chunks = []
    for i in range(0, len(flat_bytes), chunk_size_bytes):
        chunk = flat_bytes[i:i+chunk_size_bytes]
        encoded = rs.encode(chunk.tobytes())
        encoded_chunks.append(np.frombuffer(encoded, dtype=np.uint8))
    encoded_bytes = np.concatenate(encoded_chunks)

    bits = np.unpackbits(encoded_bytes, bitorder='big')
    symbols = digital_modulation(bits)

    if c == 0:
        symbol_log.extend(symbols[:1000])

    # Transmit with noise chunk-wise
    received_symbols_chunks = []
    for i in range(0, len(symbols), chunk_size_bits):
        sym_chunk = symbols[i:i+chunk_size_bits]
        noisy_chunk = apply_noise(sym_chunk, snr_db=20, burst_prob=0.01, burst_strength=6)
        received_symbols_chunks.append(noisy_chunk)

    received_symbols = np.concatenate(received_symbols_chunks)

    if c == 0:
        received_symbol_log.extend(received_symbols[:1000])

    received_bits = digital_demodulation(received_symbols)
    received_bits = received_bits[:len(bits)]

    received_bytes = np.packbits(received_bits, bitorder='big')

    # RS decode chunk-wise
    decoded_bytes = []
    chunk_len = chunk_size_bytes + rs.nsym  # encoded chunk size in bytes
    for i in range(0, len(received_bytes), chunk_len):
        rs_chunk = received_bytes[i:i+chunk_len]
        try:
            decoded_chunk, _, errata_pos = rs.decode(rs_chunk.tobytes())
            print(f"Channel {c}, chunk {i//chunk_len}: RS decode success, corrected errors: {len(errata_pos)}")
        except Exception as e:
            print(f"Channel {c}, chunk {i//chunk_len}: RS decode FAILED: {e}")
            decoded_chunk = bytes([0]*chunk_size_bytes)
        decoded_bytes.append(np.frombuffer(decoded_chunk, dtype=np.uint8))

    recovered_channel_bytes = np.concatenate(decoded_bytes)[:len(flat_bytes)]
    recovered_channel = recovered_channel_bytes.reshape(channel.shape)
    received_channels.append(recovered_channel)

received_rgb_array = np.stack(received_channels, axis=2)

# Plot symbol amplitudes before and after transmission for first channel
plt.figure(figsize=(10, 4))
plt.plot(symbol_log, label="Original Symbols", alpha=0.7)
plt.plot(received_symbol_log, label="Received Symbols", alpha=0.7, linestyle='dashed')
plt.title("Symbol Amplitudes vs. Time (Channel 0, First 1000 Symbols)")
plt.xlabel("Symbol Index")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot original and received images
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.title("Original Image (RGB)")
plt.imshow(img_array_rgb)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Received Image (RGB) with RS Decoding")
plt.imshow(received_rgb_array)
plt.axis("off")

plt.tight_layout()
plt.show()
