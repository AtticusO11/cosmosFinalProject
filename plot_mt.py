import matplotlib.pyplot as plt

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
