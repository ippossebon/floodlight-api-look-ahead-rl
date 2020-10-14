"""
Graficos
"""
def plotGraphs():
    print('Gerando graficos...')

    plt.figure()
    # plt.subplot(1)
    plt.plot(link_a_rx, '-', color="#ef476f", label = "Link a") # paradise pink
    plt.plot(link_b_rx, '-', color="#ffd166", label = "Link b") # orange yellow crayola
    plt.plot(link_c_rx, '-', color="#06d6a0", label = "Link c") # caribeen green
    plt.plot(link_d_rx, '-', color="#118AB2", label = "Link d") # blue NCS
    plt.plot(link_e_rx, '-', color="#073B4C", label = "Link e") # midnight green eagle green
    plt.plot(link_f_rx, '-', color="#5f0f40", label = "Link f") # tryian purple
    plt.plot(link_g_rx, '-', color="#9A031E", label = "Link g") # ruby red
    plt.plot(link_h_rx, '-', color="#FB8B24", label = "Link h") # dark orange
    plt.plot(link_i_rx, '-', color="#E36414", label = "Link i") # spanish orange

    plt.xlabel('Step')
    plt.ylabel('Mbits/seg')

    # Set a title of the current axes.
    plt.title('Mbits/seg RX per step')

    # show a legend on the plot
    plt.legend()

    # plt.subplot(2)
    # plt.plot(rewards)
    # plt.plot(rewards)
    # plt.xlabel('Step')
    # plt.ylabel('Reward')
    # plt.title('Reward per step')

    plt.savefig('A2C_100_lr_01_gamma_096-30-set-links_usage.pdf')

    print('Grafico gerado.')
