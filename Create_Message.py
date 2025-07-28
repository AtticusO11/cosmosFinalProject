import math
symbols = [0, 2, 3]
K = 5

def create_message(symbols, K):
    L = math.ceil(math.log2(K))  # Number of bits per symbol
    bit_groups = [bin(s)[2:].zfill(L) for s in symbols]
    return ''.join(bit_groups)
message = create_message(symbols, K)
print("Recovered bitstream:", message)