# returns m(t), K = logb2 M 

import numpy as np
import matplotlib.pyplot as plt

def create_message(symbols, samples_per_symbol):
  t = np.linspace(0, len(symbols), len(symbols) * samples_per_symbol, endpoint=False)
  m_t = np.repeat(symbols, samples_per_symbol)

  return t, m_t
