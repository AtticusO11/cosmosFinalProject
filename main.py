import digital_modulation
import create_message
import digital_demodulation
import plot_m_t

message = [0,0,0,1,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,]
M = 16
sps = 100
symbols = digital_modulation.digital_modulation(message, M)

original_bit_length = len(message)

t, m_t = create_message.create_message(symbols, sps)

final = digital_demodulation.demodulation(m_t, M, sps, original_bit_length)


if ''.join(str(b) for b in message) == final:
    print("✅ Success!")

plot_m_t.plot_m_t(t, m_t)
