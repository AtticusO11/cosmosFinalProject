# choose a file!
filename = "Teachers/Josh_Hyman.jpg"
M = 16
sps = 100

import numpy as np
import cv2 as cv
from collections import Counter
import matplotlib.pyplot as plt

def encrypt_pixels(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)
    if img is None:
        print("Error: image not found")
        exit()
    shape = img.shape
    cipherpixels = ((img.flatten().astype(np.uint16) + 7) % 256).astype(np.uint8)
    return cipherpixels, shape

pixels, original_shape = encrypt_pixels(filename)

# to binary
def convert_to_bits(pixels):
    return [np.binary_repr(pixel, width=8) for pixel in pixels]

bit_list = convert_to_bits(pixels)

# to rgb groups
def chunk(bit_list):
    return [bit_list[i:i+3] for i in range(0, len(bit_list) - 2, 3)]

# test: chunked RGB pixels sent pixel by pixel, truncated to first 32 values
chunked_values = chunk(bit_list)

''' Returns decoded and decrypted image pixels and unflattens/reshapes them'''
def unchunk(chunked_values):
    return [bit for chunk in chunked_values for bit in chunk]

unchunked_values = unchunk(chunked_values)

def decrypt_decimal(unchunked_values):
    pixel_values = np.array([int(b, 2) for b in unchunked_values], dtype=np.uint16)
    return ((pixel_values - 7) % 256).astype(np.uint8)

decrypted = decrypt_decimal(unchunked_values)

# rechunked values
reconstructed_img = decrypted.reshape(original_shape)

def digital_modulation(bits, M):
    bits_per_symbol = int(np.log2(M))
    num_on_each_side = M // 2
    rep = np.concatenate((
        np.arange(-1, -1 - 2 * num_on_each_side, -2)[::-1],
        np.arange(1, 1 + 2 * num_on_each_side, 2)
    ))
    symbols = []
    for i in range(0, len(bits), bits_per_symbol):
        symbol_bits = bits[i:i + bits_per_symbol]
        symbol_bits += [0] * (bits_per_symbol - len(symbol_bits))  # pad if needed
        index = int(''.join(map(str, symbol_bits)), 2)
        symbols.append(rep[index])
    return np.array(symbols)

def create_message(symbols, samples_per_symbol):
    return (np.linspace(0, len(symbols), len(symbols)*samples_per_symbol, endpoint=False),
            np.repeat(symbols, samples_per_symbol))


def demodulation(m_t, M, samples_per_symbol, original_bit_length):
    num_on_each_side = M // 2
    rep = np.concatenate((
        np.arange(-1, -1 - 2 * num_on_each_side, -2)[::-1],
        np.arange(1, 1 + 2 * num_on_each_side, 2)
    ))
    symbol_to_index = {int(val): idx for idx, val in enumerate(rep)}
    symbols_found = [
        int(Counter(m_t[i:i+samples_per_symbol]).most_common(1)[0][0])
        for i in range(0, len(m_t), samples_per_symbol)
    ]
    demodulated = [symbol_to_index[sym] for sym in symbols_found if sym in symbol_to_index]
    final = ''.join(np.binary_repr(item, width=int(np.log2(M))) for item in demodulated)

    return final[:original_bit_length]

def modulate_pixels(pixels, M, samples_per_symbol):
    bits_per_pixel = 24  # 3 channels * 8 bits each
    all_symbols = []
    for pixel in pixels:
        pixel_bits = [int(b) for channel in pixel for b in np.binary_repr(channel, width=8)]
        all_symbols.extend(digital_modulation(pixel_bits, M))
    all_symbols = np.array(all_symbols)
    t, m_t = create_message(all_symbols, samples_per_symbol)
    return t, m_t, len(pixels) * bits_per_pixel

# demod for reshape later
def demodulate_pixels(m_t, M, samples_per_symbol, original_bit_length):
    final_bits = demodulation(m_t, M, samples_per_symbol, original_bit_length)
    pixels = []
    for i in range(0, len(final_bits), 24):
        pixel_bits = final_bits[i:i+24].ljust(24, '0')
        channels = [int(pixel_bits[j:j+8], 2) for j in range(0, 24, 8)]
        pixels.append(channels)
    return pixels

def plot_m_t(t, m_t):
    plt.plot(t, m_t)
    plt.title("m(t): Symbols vs. Time")
    plt.xlabel("Time (in terms of T)")
    plt.xlim(0,10)
    plt.ylabel("Symbol Value")
    plt.grid(True)
    plot = plt.show()

    return plot

# TEST
message = chunk(bit_list)
message = [int(b) for byte in bit_list for b in byte]
received_pixels = []  # will store demodulated pixels
rows, cols, channels = original_shape
N = rows * cols
for i, pixel_chunk in enumerate(chunked_values):
    if i >= N:
        break
    bits = ''.join(pixel_chunk)
    bit_list = [int(b) for b in bits]
    symbols = digital_modulation(bit_list, M)
    t, m_t = create_message(symbols, sps)
    recovered_bits = demodulation(m_t, M, sps, len(bit_list))
    pixel = []
    for j in range(0, len(recovered_bits), 8):
        byte = recovered_bits[j:j+8]
        pixel.append(int(byte, 2))
    received_pixels.append(pixel)
received_pixels_np = np.array(received_pixels, dtype=np.uint8)
symbols = digital_modulation(message, M)
print(f"First five bits of original: {message[:5]}")
original_bit_length = len(message)
t, m_t = create_message(symbols, sps)
final = demodulation(m_t, M, sps, original_bit_length)
print(f"First five bits of final: {final[:5]}")
if ''.join(str(b) for b in message) == final:
    print("✅ Success!")
plot_m_t(t, m_t)
original_img = cv.imread(filename, cv.IMREAD_COLOR)

# show original & reconstructed images
combined = cv.hconcat([original_img, reconstructed_img])
cv.imshow("Image Comparison", combined)
cv.waitKey(0)
cv.destroyAllWindows()
