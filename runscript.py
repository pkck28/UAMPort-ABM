from src import *
import copy, argparse
import numpy as np

parser = argparse.ArgumentParser(description='Run the simulation')
parser.add_argument('--num_itr', type=int, default=720, help='Number of iterations')
parser.add_argument('--num_pads', type=int, default=6, help='Number of pads at the hub')
parser.add_argument('--turnaround_time', type=int, default=10, help='Turnaround time at the hub')
parser.add_argument('--recharge_rate', type=int, default=5, help='Recharge rate at the hub')
args = parser.parse_args()

# Sensitivity Variables
num_pads = args.num_pads
turnaround_time = args.turnaround_time # min
recharge_rate = args.recharge_rate # units/min

# Creating the hub
num_ports = 6
pad_location, hover_location = hubTopology(num_pads, num_ports) # Hub topology
hub = Hub(pad_location, hover_location, turnaround_time)

# Creating remote ports
port_dist_center = 4.0
port_location = pol2cart(port_dist_center, np.linspace(0, 2*np.pi, num_ports, endpoint=False))
hover_location = pol2cart(port_dist_center - 0.4, np.linspace(0, 2*np.pi, num_ports, endpoint=False))
turnaround_time = 5 # min
time_to_hub = np.linspace(15, 30, num_ports, dtype=int) # min
ports = []
for i in range(num_ports):
    ports.append(Port(port_location[i,:], hover_location[i,:], num_pads, 
                      turnaround_time, time_to_hub[i]))

# Creating vehicles
max_energy = 100
discharge_rate = 1 # units/min
vehicles = []
for i in range(num_ports):
    vehicles.append(Vehicle(i, copy.deepcopy(port_location[i,:]), max_energy, recharge_rate, discharge_rate))

# Creating the model
model = Model(hub, ports, vehicles)

# Run the model
model.run(args.num_itr)
