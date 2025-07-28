import math
import cv2 as cv
import os
import time
import matplotlib.pyplot as plt
import random

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
    plt.stem(symbols, [1]*len(symbols), basefmt=" ")
    plt.title("PAM Constellation (Rectangular)")
    plt.xlabel("Symbol Index")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()


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
                cv.waitKey(2000)  # show for 2 seconds
                cv.destroyAllWindows()
                time.sleep(0.2)  # allow focus back to terminal
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

# Assign bits and symbols
L = math.ceil(math.log2(K))
bit_groups = [bin(i)[2:].zfill(L) for i in range(K)]
symbols = get_constellation(K)

# Print table
print("\nBit | Symbol | Teacher")
print("--------------------------")
for b, s, t in zip(bit_groups, symbols, teachers):
    print(f"{b} |  {s:>6} | {t}")

combined_bits = ''.join(bit_groups)
print(f"\nCombined bits: {combined_bits}")
print(f"Symbols: [{', '.join(map(str, symbols))}]")

# Modulate combined bits
mod_bit_groups, mod_symbol_indices = digital_modulation(combined_bits, K)
print(f"\nAfter modulation:")
print(f"Bit groups: {mod_bit_groups}")
print(f"Symbol indices: {mod_symbol_indices}")

# Demodulate symbols back to bits
demod_bits = digital_demodulation(mod_symbol_indices, K)
print(f"\nAfter demodulation:")
print(f"Bits: {demod_bits}")

# Recreate message bits from symbols
recreated_message = create_message(mod_symbol_indices, K)
print(f"\nRecreated message bits:")
print(recreated_message)

# Plot the PAM constellation
plot_constellation(symbols)
