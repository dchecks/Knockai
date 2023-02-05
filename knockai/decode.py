# Read the link file and decode the data

import numpy as np


def run(link_config_file):
    fuel, ign = decode(link_config_file)

    np.set_printoptions(linewidth=200)
    print(fuel)
    print(ign)

def decode(link_file):
    # Read the line that starts with [LinkMemData]
    with open(link_file, 'r') as f:
        for line in f:
            if line.startswith('[LinkMemData]'):
                data = [int(x) for x in line.split(',')[1:]]
                break

    # Get the fuel table starting at position 62, going to position 221
    fuel_data = data[60:220]
    fuel_table = np.array(fuel_data).reshape(8, 20)
    # Get the ignition table starting at position 111, going to position 156
    ignition_data = data[260:420]
    ignition_table = np.array(ignition_data).reshape(8, 20)

    return fuel_table, ignition_table


def plot(table):
    import matplotlib.pyplot as plt

    # Normalize the data to the range [0, 1]
    normalized_table = (table - table.min()) / (table.max() - table.min())

    # Plot the table with gradient coloring
    plt.imshow(normalized_table, cmap='viridis')
    plt.colorbar()
    plt.show()



if __name__ == '__main__':
    run('resources/ecu_config_files/l1.pcl')
