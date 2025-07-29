import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# digital modulation
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


# create message
def create_message(symbols, samples_per_symbol):
  t = np.linspace(0, len(symbols), len(symbols) * samples_per_symbol, endpoint=False)
  m_t = np.repeat(symbols, samples_per_symbol)

  return t, m_t

# plot message
def plot_m_t(t, m_t):
    plt.plot(t, m_t)
    plt.title("m(t): Symbols vs. Time")
    plt.xlabel("Time (in terms of T)")
    plt.ylabel("Symbol Value")
    plt.grid(True)

    plt.savefig("message_plot.png")
    print("Plot saved as message_plot.png")

    plot = plt.show()

    return plot


# digital demodulation
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


# TEST
message = [0,0,0,1,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,]
M = 16
sps = 100
symbols = digital_modulation(message, M)

original_bit_length = len(message)

t, m_t = create_message(symbols, sps)

final = demodulation(m_t, M, sps, original_bit_length)


if ''.join(str(b) for b in message) == final:
    print("✅ Success!")

plot_m_t(t, m_t)
