import math
import cv2 as cv
import os
import time
import matplotlib.pyplot as plt
import random
import reedsolo
from reedsolo import RSCodec

# Dictionary of teacher names (lowercase) mapped to image paths
teachers_dict = {
    'ethan ge': 'Teachers/Ethan_Ge.jpg',
    'lev tauz': 'Teachers/Lev_Tauz.jpg',
    'professor dolecek': 'Teachers/Professor_Dolecek.jpg',
    'professor roberts': 'Teachers/Professor_Roberts.jpg',
}

def digital_modulation(bits, num_symbols):
    L = math.ceil(math.log2(num_symbols))
    if len(bits) % L != 0:
        bits += '0' * (L - len(bits) % L)  # pad bits
    bit_groups = []
    symbol_indices = []
    for i in range(0, len(bits), L):
        group = bits[i:i+L]
        bit_groups.append(group)
        symbol_index = int(group, 2)
        symbol_indices.append(symbol_index)
    return bit_groups, symbol_indices

def digital_demodulation(symbol_indices, num_symbols):
    L = math.ceil(math.log2(num_symbols))
    bit_groups = [bin(index)[2:].zfill(L) for index in symbol_indices]
    return ''.join(bit_groups)

def create_message(symbol_indices, K):
    L = math.ceil(math.log2(K))
    bit_groups = [bin(s)[2:].zfill(L) for s in symbol_indices]
    return ''.join(bit_groups)

def get_constellation(m):
    step = 2
    start = -((m - 1) * step) // 2
    return [start + step * i for i in range(m)]

def plot_constellation(symbols):
    heights = [random.uniform(0.5, 1.5) for _ in symbols]
    plt.stem(symbols, heights, basefmt=" ")
    plt.title("PAM Constellation (Rectangular)")
    plt.xlabel("Symbol Index")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()

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

# --- Main program ---
teachers = []
print("Type teacher names one by one (leave blank to finish):")
while True:
    name = input("> ").strip()
    if name == "":
        break
    teachers.append(name)
    key = name.lower()
    if key in teachers_dict:
        img_path = teachers_dict[key]
        if os.path.exists(img_path):
            img = cv.imread(img_path)
            if img is not None:
                cv.imshow(name, img)
                cv.waitKey(2000)
                cv.destroyAllWindows()
                time.sleep(0.2)
                print(f"Displayed image for {name}")
            else:
                print(f"⚠️ Failed to load image for {name}")
        else:
            print(f"⚠️ Image file not found for {name}")
    else:
        print(f"No image found for {name}")

K = len(teachers)
if K == 0:
    print("No teachers entered.")
    exit()

L = math.ceil(math.log2(K))
bit_groups = [bin(i)[2:].zfill(L) for i in range(K)]
symbols = get_constellation(K)

print("\nBit | Symbol | Teacher")
print("--------------------------")
for b, s, t in zip(bit_groups, symbols, teachers):
    print(f"{b} |  {s:>6} | {t}")

combined_bits = ''.join(bit_groups)
print(f"\nCombined bits: {combined_bits}")
print(f"Symbols: [{', '.join(map(str, symbols))}]")

# RS encode
encoded_bytes = rs_encode(combined_bits)
encoded_bits = ''.join(format(b, '08b') for b in encoded_bytes)

# Modulate RS-encoded bits
mod_bit_groups, mod_symbol_indices = digital_modulation(encoded_bits, K)
print(f"\nAfter modulation:")
print(f"Bit groups: {mod_bit_groups}")
print(f"Symbol indices: {mod_symbol_indices}")

# Demodulate
demod_bits = digital_demodulation(mod_symbol_indices, K)

# Convert demodulated bits back to bytes for RS decoding
byte_array = bytearray(int(demod_bits[i:i+8], 2) for i in range(0, len(demod_bits), 8))

# RS decode
decoded_bytes = rs_decode(byte_array)

# Convert decoded bytes back to bit string
recovered_bits = ''.join(format(b, '08b') for b in decoded_bytes)

# Regroup bits into symbols
recreated_bit_groups = [recovered_bits[i:i+L] for i in range(0, len(recovered_bits), L)]
recovered_symbol_indices = [int(bg, 2) for bg in recreated_bit_groups]

print(f"\nAfter demodulation:")
print(f"Bits: {demod_bits}")
print(f"\nRecreated message bits:")
print(recovered_bits)

# Plot the PAM constellation
plot_constellation(symbols)
