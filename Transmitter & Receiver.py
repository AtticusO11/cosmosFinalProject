fs = 0
ts = 0
received_symbols = 0




if True:
    tx = Pluto("usb:0.4.5")
    rx = tx
else:
    tx = Pluto("usb:1.12.5")
    rx = Pluto()
print('Number of receive symbols: ', len(received_symbols))