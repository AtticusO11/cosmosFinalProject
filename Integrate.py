import cv2 as cv
import os
import math

teachers = [
    'Teachers/Ethan_Ge.jpg',
    'Teachers/Lev_Tauz.jpg',
    'Teachers/Professor_Dolecek.jpg',
    'Teachers/Professor_Roberts.jpg',
    'Teachers/Samuel_Li.jpg',
    'Teachers/Josh_Hyman.jpg'
]

def bits_to_symbol_indices(bits, num_symbols):
    L = int(math.log2(num_symbols))
    if len(bits) % L != 0:
        bits += '0' * (L - len(bits) % L)  # pad bits
    
    symbols = []
    for i in range(0, len(bits), L):
        group = bits[i:i+L]
        symbol_index = int(group, 2)
        symbols.append(symbol_index)
    return symbols

def show_teacher_by_index(index):
    if 0 <= index < len(teachers):
        path = teachers[index]
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return
        img = cv.imread(path)
        if img is None:
            print(f"⚠️ Failed to load image {path}")
        else:
            cv.imshow(f"Teacher {index}", img)
            cv.waitKey(0)
            cv.destroyAllWindows()
    else:
        print("Teacher index out of range")

# Example usage
num_teachers = len(teachers)
bits = input("Enter binary bits to select teachers: ").strip()
symbol_indices = bits_to_symbol_indices(bits, num_teachers)

for idx in symbol_indices:
    show_teacher_by_index(idx)
