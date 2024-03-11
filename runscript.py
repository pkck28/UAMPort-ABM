from src import *
import copy, argparse
import numpy as np

parser = argparse.ArgumentParser(description='Run the simulation')
parser.add_argument('--num_itr', type=int, default=100, help='Number of iterations')
parser.add_argument('--num_pads', type=int, default=2, help='Number of pads at the hub')
parser.add_argument('--num_ports', type=int, default=6, help='Number of remote ports')
args = parser.parse_args()

# Variables
num_pads = args.num_pads
num_ports = args.num_ports

# Creating the hub
pad_location, hover_location = hubTopology(num_pads, num_ports) # Hub topology
turnaround_time = 10 # min
inter_arrivel_time = 1 # min
hub = Hub(pad_location, hover_location, turnaround_time, inter_arrivel_time)

# Creating remote ports
port_dist_center = 4.0
port_location = pol2cart(port_dist_center, np.linspace(0, 2*np.pi, num_ports, endpoint=False))
hover_location = pol2cart(port_dist_center - 0.4, np.linspace(0, 2*np.pi, num_ports, endpoint=False))
turnaround_time = 5 # min
inter_arrivel_time = 1 # min
time_to_hub = np.linspace(15, 30, num_ports, dtype=int) # min
ports = []
for i in range(num_ports):
    ports.append(Port(port_location[i,:], hover_location[i,:], num_pads, 
                      turnaround_time, inter_arrivel_time, time_to_hub[i]))

# Creating vehicles
max_energy = 75
discharge_rate = 1 # units/min
recharge_rate = 2 # units/min
vehicles = []
for i in range(num_ports):
# for i in range(2):
    vehicles.append(Vehicle(i, copy.deepcopy(port_location[i,:]), max_energy, recharge_rate, discharge_rate))

# Creating the model
model = Model(hub, ports, vehicles)

# Run the model
model.run(args.num_itr)
