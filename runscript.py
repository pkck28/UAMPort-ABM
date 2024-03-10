from src import *
import copy, argparse
import numpy as np

parser = argparse.ArgumentParser(description='Run the simulation')
parser.add_argument('--num_itr', type=int, default=720, help='Number of iterations')
parser.add_argument('--num_pads', type=int, default=1, help='Number of pads at the hub')
args = parser.parse_args()

# Creating the hub
num_pads = args.num_pads
turnaround_time = 10 # min
hub_location = np.array([0.0, 0.0]) # center of the grid
hover_location = np.array([[0.45, 0.0], [0.0, 0.45], [-0.45, 0.0], [0.0, -0.45]])

hub = Hub(hub_location, hover_location, num_pads, turnaround_time)

# Creating remote pads
pad_location = np.array([[2.0, 0.0], [0.0, 2.0], [-2.0, 0.0], [0.0, -2.0]])
hover_location = np.array([[1.75, 0.0], [0.0, 1.75], [-1.75, 0.0], [0.0, -1.75]])
num_pads= 1 # fixed
turnaround_time = 5 # min
time_to_hub = [15, 20, 25, 30] # min
port = []
for i in range(pad_location.shape[0]):
    port.append(Port(pad_location[i,:], hover_location[i,:], num_pads, turnaround_time, time_to_hub[i]))

# Creating vehicles
max_energy = 75
recharge_rate = 3 # units/min
vehicle = []
for i in range(4):
    vehicle.append(Vehicle(i, copy.deepcopy(pad_location[i,:]), max_energy, recharge_rate))

# Creating the model
model = Model(hub, port, vehicle)

# Setting model parameters
model.iterations = args.num_itr

model.run()
