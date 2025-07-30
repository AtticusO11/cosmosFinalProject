import numpy as np
import cv2 as cv
from collections import Counter
import matplotlib.pyplot as plt

# choose a file!
filename = "Teachers/Josh_Hyman.jpg"

def encrypt_pixels(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)

    if img is None:
        print("Error: image not found")
        exit()

    shape = img.shape
    pixels = img.flatten()

    # not encrypted pixels
    #print(pixels)

    # Convert to a larger integer type to avoid overflow on addition
    pixels_int = pixels.astype(np.uint16)

    # Caesar cipher +7 encryption with no overflow
    cipherpixels = (pixels_int + 7) % 256

    # Cast back to uint8
    cipherpixels = cipherpixels.astype(np.uint8)

    #print(cipherpixels)
    return cipherpixels, shape


pixels, original_shape = encrypt_pixels(filename)


def convert_to_bits(pixels):
    bitstream = ''.join(np.binary_repr(pixel, width = 8) for pixel in pixels)

    total_bit_list = [] # list of 8-bit values
    current_bit_list = []
    for bit in bitstream:
        current_bit_list.append(bit)
        if len(current_bit_list) == 8:
            total_bit_list.append(''.join(current_bit_list))
            current_bit_list = []

    return total_bit_list

bit_list = convert_to_bits(pixels)

def chunk(bit_list):
    pixels = []
    for i in range(0, len(bit_list), 3):
        pixel_chunk = bit_list[i: i + 3]
        if len(pixel_chunk) == 3:
            pixels.append(pixel_chunk)

    return pixels

# test: chunked RGB pixels sent pixel by pixel, truncated to first 32 values
chunked_values = chunk(bit_list)


''' Returns decoded and decrypted image pixels and unflattens/reshapes them'''
def unchunk(chunked_values):
    unchunked_values = [bit for chunk in chunked_values for bit in chunk]

    return unchunked_values

unchunked_values = unchunk(chunked_values)

def decrypt_decimal(unchunked_values):
    pixel_values = np.array([int(b, 2) for b in unchunked_values], dtype = np.uint16)

    decrypted = (pixel_values - 7) % 256
    decrypted = decrypted.astype(np.uint8)

    return decrypted

decrypted = decrypt_decimal(unchunked_values)

# rechunked values
reconstructed_img = decrypted.reshape(original_shape)

def digital_modulation(bits, M):
    bits_per_symbol = int(np.log2(M))

    num_on_each_side = M//2
    rep_left = np.arange(-1, -1-2*num_on_each_side, -2)
    rep_left = np.flip(rep_left)
    rep_right = np.arange(1, 1+2*num_on_each_side, 2)
    rep = np.concatenate((rep_left, rep_right))

    symbols = []
    mapping = {}
    empty = []

    for i in range(0, len(bits), bits_per_symbol):
        symbol_bits = bits[i: i + bits_per_symbol]

        if len(symbol_bits) < bits_per_symbol:
            symbol_bits += [0] * (bits_per_symbol - len(symbol_bits))

        bitstring = ''.join(str(b) for b in symbol_bits)
        index = int(bitstring, 2)
        mapping[index] = rep[index]
        empty.append(mapping[index])

    symbols = np.array(empty)
    
    return symbols

def create_message(symbols, samples_per_symbol):
    t = np.linspace(0, len(symbols), len(symbols)*samples_per_symbol, endpoint=False)
    m_t = np.repeat(symbols, samples_per_symbol)
    return t, m_t

def demodulation(m_t, M, samples_per_symbol, original_bit_length):
    symbols_found = []
    for i in range(0, len(m_t), samples_per_symbol):
        chunk = m_t[i:i+samples_per_symbol]
        counts = Counter(chunk)
        majority_symbol, _ = counts.most_common(1)[0]
        symbols_found.append(int(majority_symbol))

    num_on_each_side = M//2
    rep_left = np.arange(-1, -1-2*num_on_each_side, -2)
    rep_left = np.flip(rep_left)
    rep_right = np.arange(1, 1+2*num_on_each_side, 2)
    rep = np.concatenate((rep_left, rep_right))

    symbol_to_index = {int(val): idx for idx, val in enumerate(rep)}

    demodulated = []
    final = []
    for sym in symbols_found:
        if sym in symbol_to_index:
            demodulated.append(symbol_to_index[sym])

    for item in demodulated:
        final.append(np.binary_repr(item, width=int(np.log2(M))))

    final = ''.join(final)
    if original_bit_length != len(final):
        final = final[:original_bit_length]
    return final


def modulate_pixels(pixels, M, samples_per_symbol):
    bits_per_pixel = 24  # 8 bits per channel * 3 channels (RGB)
    bits_per_symbol = int(np.log2(M))
    symbols_per_pixel = bits_per_pixel // bits_per_symbol  # how many symbols per pixel

    all_symbols = []

    for pixel in pixels:
        pixel_bits = []
        for channel in pixel:
            pixel_bits.extend([int(b) for b in np.binary_repr(channel, width=8)])

        symbols = digital_modulation(pixel_bits, M)
        all_symbols.extend(symbols)

    all_symbols = np.array(all_symbols)
    t, m_t = create_message(all_symbols, samples_per_symbol)
    return t, m_t, len(pixels) * bits_per_pixel

# demod for reshape later
def demodulate_pixels(m_t, M, samples_per_symbol, original_bit_length):
    final_bits = demodulation(m_t, M, samples_per_symbol, original_bit_length)
    pixels = []
    for i in range(0, len(final_bits), 24):
        pixel_bits = final_bits[i:i+24]
        if len(pixel_bits) < 24:
            pixel_bits += '0' * (24 - len(pixel_bits))

        channels = []
        for j in range(0, 24, 8):
            byte = pixel_bits[j:j+8]
            channels.append(int(byte, 2))
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

M = 16
sps = 100

received_pixels = []  # will store demodulated pixels

rows, cols, channels = original_shape
N = rows * cols  # adjust as needed

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
