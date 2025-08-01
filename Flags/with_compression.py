# choose a file!
#filename = "Flags/Iceland.png"
filename = "Teachers/Sonic.jpg"
#filename = "Teachers/Yoda.jpg"
M = 16
sps = 100

import numpy as np
import cv2 as cv
from collections import Counter
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# lz Compression & Decompression
# ---------------------------------------------------------------
def lz_compress(bit_string):
    dictionary = {}
    output = []
    w = ""
    dict_size = 1
    for c in bit_string:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            output.append((dictionary.get(w, 0), c))
            dictionary[wc] = dict_size
            dict_size += 1
            w = ""
    if w:
        output.append((dictionary.get(w, 0), ''))
    return output

def lz_decompress(compressed):
    dictionary = {0: ""}
    output = []
    dict_size = 1
    for index, char in compressed:
        entry = dictionary.get(index, '') + char
        output.append(entry)
        dictionary[dict_size] = entry
        dict_size += 1
    return ''.join(output)

def compressed_to_bits(compressed):
    bits = ''
    max_index = max((i for i, _ in compressed), default=0)
    index_bit_len = max(1, int(np.ceil(np.log2(max_index + 1))))
    for index, char in compressed:
        bits += np.binary_repr(index, width=index_bit_len)
        bits += char
    return bits, index_bit_len

def bits_to_compressed(bits, index_bit_len):
    compressed = []
    i = 0
    while i + index_bit_len < len(bits):
        index = int(bits[i:i+index_bit_len], 2)
        i += index_bit_len
        if i >= len(bits): break
        char = bits[i]
        compressed.append((index, char))
        i += 1
    return compressed

# ---------------------------------------------------------------
# Image Encryption
# ---------------------------------------------------------------
def encrypt_pixels(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)
    if img is None:
        print("Error: image not found")
        exit()
    shape = img.shape
    cipherpixels = ((img.flatten().astype(np.uint16) + 7) % 256).astype(np.uint8)
    return cipherpixels, shape

def convert_to_bits(pixels):
    return [np.binary_repr(pixel, width=8) for pixel in pixels]

def chunk(bit_list):
    return [bit_list[i:i+3] for i in range(0, len(bit_list) - 2, 3)]

def unchunk(chunked_values):
    return [bit for chunk in chunked_values for bit in chunk]

def decrypt_decimal(unchunked_values):
    pixel_values = np.array([int(b, 2) for b in unchunked_values], dtype=np.uint16)
    return ((pixel_values - 7) % 256).astype(np.uint8)

# ---------------------------------------------------------------
# Digital Modulation & Demodulation
# ---------------------------------------------------------------
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
        symbol_bits += [0] * (bits_per_symbol - len(symbol_bits))
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

# ---------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------
def plot_m_t(t, m_t):
    plt.plot(t, m_t)
    plt.title("m(t): Symbols vs. Time")
    plt.xlabel("Time (in terms of T)")
    plt.xlim(0, 50)
    plt.ylabel("Symbol Value")
    plt.grid(True)
    plt.show()

# ---------------------------------------------------------------
# MAIN TEST BLOCK
# ---------------------------------------------------------------
pixels, original_shape = encrypt_pixels(filename)
bit_list = convert_to_bits(pixels)
bit_string = ''.join(bit_list)

compressed = lz_compress(bit_string)
compressed_bits, index_bit_len = compressed_to_bits(compressed)
message = [int(b) for b in compressed_bits]

symbols = digital_modulation(message, M)
original_bit_length = len(compressed_bits)
t, m_t = create_message(symbols, sps)

demodulated_bits = demodulation(m_t, M, sps, original_bit_length)
recovered_compressed = bits_to_compressed(demodulated_bits, index_bit_len)
final = lz_decompress(recovered_compressed)

# decrypt and reshape
unchunked_values = convert_to_bits(decrypt_decimal(convert_to_bits(pixels)))  # just to get reshaped
decrypted = decrypt_decimal(final[i:i+8] for i in range(0, len(final), 8))
# pad final bitstring to be multiple of 8
if len(final) % 8 != 0:
    final += '0' * (8 - len(final) % 8)

pixels_flat = np.array([int(final[i:i+8], 2) for i in range(0, len(final), 8)], dtype=np.uint16)
pixels_flat = ((pixels_flat - 7) % 256).astype(np.uint8)

needed = np.prod(original_shape)
if len(pixels_flat) < needed:
    pixels_flat = np.pad(pixels_flat, (0, needed - len(pixels_flat)), constant_values=0)

reconstructed_img = pixels_flat.reshape(original_shape)

# plot & display
plot_m_t(t, m_t)
original_img = cv.imread(filename, cv.IMREAD_COLOR)
combined = cv.hconcat([original_img, reconstructed_img])
cv.imshow("Image Comparison", combined)
cv.waitKey(0)
cv.destroyAllWindows()
