import math

teachers = [
    ('Ethan Ge', 'Teachers/Ethan_Ge.jpg'),
    ('Lev Tauz', 'Teachers/Lev_Tauz.jpg'),
    ('Professor Dolecek', 'Teachers/Professor_Dolecek.jpg'),
    ('Professor Roberts', 'Teachers/Professor_Roberts.jpg'),
    ('Samuel Li', 'Teachers/Samuel_Li.jpg')
]

def digital_modulation(num_symbols):
    L = math.ceil(math.log2(num_symbols))
    total = 2 ** L
    
    bit_groups = []
    symbol_indices = []
    
    for symbol_index in range(total):
        bits = bin(symbol_index)[2:].zfill(L)
        bit_groups.append(bits)
        symbol_indices.append(symbol_index)
    
    return bit_groups, symbol_indices

bit_groups, symbol_indices = digital_modulation(len(teachers))

print(f"Bits:    [{', '.join(bit_groups)}]")
print(f"Symbols: [{', '.join(map(str, symbol_indices))}]")
