import numpy as np
from collections import Counter

def demodulation(m_t, M, samples_per_symbol, original_bit_length):
    symbols_found = []
    for i in range(0, len(m_t), samples_per_symbol):
        chunk = m_t[i:i+samples_per_symbol]
        counts = Counter(chunk)
        majority_symbol, count = counts.most_common(1)[0]
        symbols_found.append(int(majority_symbol))
    print(f"Symbols found: {symbols_found}")

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
    print(f"Demodulated (decimal): {demodulated}")
            
    for item in demodulated:
        final.append(np.binary_repr(item, width = int(np.log2(M))))
    
    final = ''.join(final)
    if original_bit_length != len(final):
        final = final[:original_bit_length]
    print(f"Final Bits: {final}")

    return final
    
    
