import cv2 as cv
import os
import math

# Make sure keys are all lowercase to match user input
teachers = {
    'ethan ge': 'Teachers/Ethan_Ge.jpg',
    'lev tauz': 'Teachers/Lev_Tauz.jpg',
    'professor dolecek': 'Teachers/Professor_Dolecek.jpg',
    'professor roberts': 'Teachers/Professor_Roberts.jpg',
    'samuel li': 'Teachers/Samuel_Li.jpg'
}

def digital_modulation(bits, M):
    import math
    L = int(math.log2(M))
    bit_groups = [bits[i:i+L] for i in range(0, len(bits), L)]
    symbols = []
    N = 0  # total symbols output
    
    for i in range(0, len(bits), L):
        group = bits[i:i+L]
        symbol_index = int(group, 2)
        symbols.append(symbol_index)
        N += 1  # increment count for each symbol output
    
    print(f"Total symbols output: {N}")
    print(f"L = {L}")
    print(f"bits = {bit_groups}")
    return symbols
def get_constellation(M):
    pass


bits = "11010011"
print(f"Bits = {bits}")
M = 4  # QPSK: 2 bits per symbol
symbols = digital_modulation(bits, M)
print(f"Symbols: {symbols}")



# Get user input, normalized
name_input = input("Enter the teacher's name: ").strip().lower()

if name_input in teachers:
    path = teachers[name_input]

    if not os.path.exists(path):
        print(f"File not found: {path}")
    else:
        img = cv.imread(path)
        if img is None:
            print(f"⚠️ Failed to load image data for {name_input}")
        else:
            print(f"Showing an image of {name_input.title()}")
            cv.imshow(name_input.title(), img)
            cv.waitKey(0)
            cv.destroyAllWindows()
else:
    print("Name not recognized. Try one of these:")
    for key in teachers:
        print(f" - {key.title()}")
