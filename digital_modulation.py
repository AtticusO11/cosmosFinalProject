import numpy as np

def digital_modulation(bits, M):
  print("Original Bits: " + ''.join(str(b) for b in bits))
  symbols = []
  mapping = {}
  empty= []

  bits_per_symbol = int(np.log2(M))

  num_on_each_side = M//2
  rep_left = np.arange(-1, -1-2*num_on_each_side, -2)
  rep_left = np.flip(rep_left)
  rep_right = np.arange(1, 1+2*num_on_each_side, 2)
  rep = np.concatenate((rep_left, rep_right))

  for i in range(0, len(bits), bits_per_symbol):
    symbol_bits = bits[i: (i + bits_per_symbol)]


    if len(symbol_bits) < (bits_per_symbol):
      symbol_bits += [0] * (bits_per_symbol - len(symbol_bits))

    #print(symbol_bits)
    bitstring = ''.join(str(b) for b in symbol_bits)


    symbols.append(int(bitstring, 2))
    index = int(bitstring, 2)
    mapping[index] = rep[index]
    empty.append(mapping[index])

  #print(mapping)

  symbols = np.array(empty)
  print(f"Symbols: {symbols}")

  return symbols
