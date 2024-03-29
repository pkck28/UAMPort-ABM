# Classes for the model, vehicle, ports and hub
# Unit of analysis: minute

import matplotlib.pyplot as plt
import numpy as np
import copy, os
import imageio.v2 as imageio

class Vehicle():

    def __init__(self, id, location, max_energy, recharge_rate, discharge_rate):

        self.id = id
        self.location = location
        self.max_energy = max_energy # units
        self.avail_energy = copy.deepcopy(max_energy) # units
        self.recharge_rate = recharge_rate # units/min
        self.discharge_rate = discharge_rate # units/min

class Hub():

    def __init__(self, location, hover_location, turnaround_time):

        self.location = location
        self.hover_location = hover_location
        self.num_pads = location.shape[0]
        self.turnaround_time = turnaround_time

class Port():

    def __init__(self, location, hover_location, num_pads, turnaround_time, time_to_hub):

        self.location = location
        self.hover_location = hover_location
        self.num_pads = num_pads
        self.turnaround_time = turnaround_time
        self.time_to_hub = time_to_hub

class Model():

    def __init__(self, hub, ports, vehicles):
        """
            Method to initialize the model

            Parameters
            ----------
            hub : class
                Hub class
            ports : list
                List of port classes
            vehicles : list
                List of vehicle classes
        """

        # Instance variables
        self.hub = hub
        self.ports = ports
        self.vehicles = vehicles

        # Assigning the initial variables for the hub
        self.hub.avail_pads = np.linspace(1, self.hub.location.shape[0], self.hub.location.shape[0], dtype=int).tolist()
        self.hub.takeoff = 0
        self.hub.land = 0
        self.hub.queue = []

        # Assigning the initial variables for the ports
        for port in self.ports:
            port.avail_pads = [] # Since vehicles are occupying the pads
            port.takeoff = 0
            port.land = 0
            port.queue = []

        # Assigning the initial variables for the vehicles
        for vehicle in self.vehicles:
            vehicle.destination = None
            vehicle.pad = 1
            vehicle.wait_time = 0
            vehicle.status = 'ground'
            vehicle.trip = 0
            vehicle.travel_time = self.ports[vehicle.id].time_to_hub
            vehicle.dx = (self.hub.hover_location[vehicle.id,0] - vehicle.location[0])/vehicle.travel_time
            vehicle.dy = (self.hub.hover_location[vehicle.id,1] - vehicle.location[1])/vehicle.travel_time

    def run(self, iterations):
        """
            Method to run the simulation

            Parameters
            ----------
            iterations : int
                Number of iterations
        """

        # Creating directory for storing the results
        self.directory = f'output_{self.hub.num_pads}_{self.hub.turnaround_time}_{self.vehicles[0].recharge_rate}'
        if not os.path.isdir(self.directory):
            os.system("mkdir {}".format(self.directory))
        else:
            os.system("rm -r {}".format(self.directory))
            os.system("mkdir {}".format(self.directory))
        images = []

        # Simlulation loop
        for i in range(iterations+1):

            # Plotting
            self.plot(i)

            # Images
            images.append(imageio.imread(self.directory+'/iteration'+str(i+1)+'.png'))

            if np.min([vehicle.avail_energy for vehicle in self.vehicles]) < 0:
                print('Energy level is below 0. Simulation stopped at iteration: {}'.format(i))
                break

            # Vehicle position updated asynchronusly
            for vehicle in self.vehicles:

                # Vehicle is on the ground and ready to liftoff
                if vehicle.status == 'ground' and vehicle.wait_time == 0:

                    # Only takeoff if vehicle has enough energy for round trip
                    if isinstance(vehicle.destination, Hub) and vehicle.avail_energy < 3.0*self.ports[vehicle.id].time_to_hub:
                            vehicle.avail_energy = min(vehicle.avail_energy + vehicle.recharge_rate, vehicle.max_energy)

                    else:

                        if isinstance(vehicle.destination, Hub):
                            # Updating the hub variables
                            self.hub.takeoff += 1
                            self.hub.avail_pads.append(vehicle.pad)

                            # Takeoff to hover location
                            vehicle.location[0] = self.hub.hover_location[vehicle.id,0]
                            vehicle.location[1] = self.hub.hover_location[vehicle.id,1]

                            # Setting the next destination
                            vehicle.destination = self.ports[vehicle.id]
                            vehicle.travel_time = self.ports[vehicle.id].time_to_hub
                            vehicle.dx = (vehicle.destination.hover_location[0] - vehicle.location[0])/vehicle.travel_time
                            vehicle.dy = (vehicle.destination.hover_location[1] - vehicle.location[1])/vehicle.travel_time

                        else:
                            # Updating the port variables
                            self.ports[vehicle.id].takeoff += 1
                            self.ports[vehicle.id].avail_pads.append(vehicle.pad)

                            # Takeoff to hover location
                            vehicle.location[0] = self.ports[vehicle.id].hover_location[0]
                            vehicle.location[1] = self.ports[vehicle.id].hover_location[1]
                            
                            # Setting the next destination
                            vehicle.destination = self.hub
                            vehicle.travel_time = self.ports[vehicle.id].time_to_hub
                            vehicle.dx = (vehicle.destination.hover_location[vehicle.id,0] - vehicle.location[0])/vehicle.travel_time
                            vehicle.dy = (vehicle.destination.hover_location[vehicle.id,1] - vehicle.location[1])/vehicle.travel_time

                        vehicle.avail_energy -= vehicle.discharge_rate/2 # discharge rate is half when taking off
                        vehicle.status = 'flight'

                # Vehicle is on the ground until turnaround time
                elif vehicle.status == 'ground' and vehicle.wait_time > 0:

                    vehicle.wait_time -= 1 # decrementing the wait time
                    
                    # Recharge the vehicle if it is at the hub
                    if isinstance(vehicle.destination, Hub) and vehicle.avail_energy < vehicle.max_energy:
                        vehicle.avail_energy = min(vehicle.avail_energy + vehicle.recharge_rate, vehicle.max_energy)

                # Vehicle has reached the destination's hover location
                elif vehicle.status == 'flight' and vehicle.travel_time == 0:

                    vehicle.avail_energy -= vehicle.discharge_rate/2 # discharge rate is half when hovering/landing
                    
                    # Adding to the queue
                    if vehicle.id not in vehicle.destination.queue:
                        vehicle.destination.queue.append(vehicle.id)

                    # Land if a pad is available and next in queue or else hover
                    if len(vehicle.destination.avail_pads) > 0 and vehicle.id == vehicle.destination.queue[0]:

                        vehicle.status = 'ground'
                        vehicle.trip += 1
                        vehicle.wait_time = vehicle.destination.turnaround_time
                        vehicle.destination.land += 1
                        vehicle.destination.queue.remove(vehicle.id)
                        vehicle.pad = vehicle.destination.avail_pads.pop(0) # Removing the pad number from the available pads and assign to vehicle

                        # Moving vehicle to assigned pad
                        if isinstance(vehicle.destination, Hub):
                            vehicle.location[0] = vehicle.destination.location[vehicle.pad-1,0]
                            vehicle.location[1] = vehicle.destination.location[vehicle.pad-1,1]
                        else:
                            vehicle.location[0] = vehicle.destination.location[0]
                            vehicle.location[1] = vehicle.destination.location[1]

                # Vehicle is flying towards destination
                elif vehicle.status == 'flight' and vehicle.travel_time > 0:

                    vehicle.location[0] += vehicle.dx
                    vehicle.location[1] += vehicle.dy
                    vehicle.travel_time -= 1
                    vehicle.avail_energy -= vehicle.discharge_rate

        imageio.mimsave(self.directory+'/animation.gif', images, format='.gif', fps=2.0, loop=0)
            
    def plot(self, i=None):
        """
            Method to plot all the entities within simulation
        """
        
        color = ['r', 'b', 'g', 'm', 'k', 'c']
        pad_radius = 0.3
        hub_pad_radius = 0.4

        fig, ax = plt.subplots(figsize=(8, 8))

        # Plotting the hub
        for index in range(self.hub.num_pads):
            pad = self.hub.location[index,:]
            circle = plt.Circle((pad[0], pad[1]), hub_pad_radius, fill=False)
            ax.add_patch(circle)
            ax.annotate(index+1, (pad[0], pad[1]), va="center", ha="center", fontsize=14)
        circle = plt.Circle((0, 0), self.hub.hover_location[0,0]+0.15, fill=False, linestyle='--')
        ax.add_patch(circle)
        ax.annotate('HUB', (0, 0), va="center", ha="center", fontsize=14, fontweight='bold')

        # Plotting the ports
        for index, port in enumerate(self.ports):
            circle = plt.Circle((port.location[0], port.location[1]), pad_radius, fill=True, color=color[index], alpha=0.2)
            ax.add_patch(circle)
            ax.annotate(index+1, (port.location[0], port.location[1]), va="center", ha="center", fontsize=14)
            ax.plot(self.hub.hover_location[index,0], self.hub.hover_location[index,1], 'kx')
            ax.plot(port.hover_location[0], port.hover_location[1], 'kx')

        # Plotting the vehicles
        for index, vehicle in enumerate(self.vehicles):

            ax.quiver(vehicle.location[0], vehicle.location[1], vehicle.dx, vehicle.dy,
                        angles='xy', zorder=10, color=color[index], headlength=5, headwidth=4, 
                        headaxislength=5, pivot="middle", alpha=0.6, label=f'Vehicle {index+1}: {vehicle.trip} trips')

            # Annotate charge level
            ax.annotate(vehicle.avail_energy, (vehicle.location[0]+0.1, vehicle.location[1]+0.1), va="bottom", 
                        ha="left", fontsize=10)

        # Add no of takeoffs and landings
        bbox_props = dict(boxstyle="round, pad=0.3", fc="w", ec="k", lw=0.72)
        msg = f'# of T/LO operations\nHub: T={self.hub.takeoff}, LO={self.hub.land}'
        for index, port in enumerate(self.ports):
            msg += f'\nPort {index+1}: T={port.takeoff}, LO={port.land}'
        ax.annotate(msg, (3.5, -1.8), va="center", ha="center", fontsize=12, bbox=bbox_props)

        # Adding a note
        ax.annotate('Number near vehicle\ndenotes energy level', (-3.5, -2.0), va="center", 
                    ha="center", fontsize=12, bbox=bbox_props)
        ax.annotate('\'x\' denotes\nhover location', (-3.5, -1.2), va="center", 
                    ha="center", fontsize=12, bbox=bbox_props)
        ax.annotate(f'Turnaround time \nat hub: {self.hub.turnaround_time} min', (3.5, 2.2), va="center", 
                    ha="center", fontsize=12, bbox=bbox_props)
        ax.annotate(f'Recharge rate:\n{self.vehicles[0].recharge_rate} units/min', (3.5, 1.5), va="center",
                    ha="center", fontsize=12, bbox=bbox_props)
        # ax.annotate(f'Queue: {self.hub.queue}\nAvail pads: {self.hub.avail_pads}', (0.0, -3.5), va="center", ha="center", fontsize=12, bbox=bbox_props)

        # Asthetics
        if i is not None:
            ax.set_title('UAM Dashboard - Time: {}'.format(itr2time(i)))
        ax.axis('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.legend(loc=(0.01, 0.58), fontsize=12)
        fig.tight_layout()
        plt.savefig(f'{self.directory}/iteration{i+1}.png')
        plt.close()

def pol2cart(rho, phi):
    """
        Function to convert polar coordinates to cartesian coordinates

        Parameters
        ----------
        rho : float
            Distance from the origin
        phi : float
            Angle in radians
        
        Returns
        -------
        numpy array
    """    

    x = rho * np.cos(phi)
    y = rho * np.sin(phi)

    return np.hstack(( x.reshape(-1,1), y.reshape(-1,1) ))

def hubTopology(num_pads, num_ports):
    """
        Function to create the hub topology based on
        takeoff & landing pads and number of remote ports

        Parameters
        ----------
        num_pads : int
            Number of pads
        num_ports : int
            Number of remote ports
            
        Returns
        -------
        pad_location : numpy array
            Location of the pads within hub
        hover_location : numpy array
            Location of the hover points around hub
    """

    if num_pads == 1:
        pad_location = np.array([[0.0, 0.0]])
    else:
        pad_location = pol2cart(0.8, np.linspace(0, 2*np.pi, num_pads, endpoint=False))

    hover_location = pol2cart(1.4, np.linspace(0, 2*np.pi, num_ports, endpoint=False))

    return pad_location, hover_location

def itr2time(min):
    """
        Function to convert iteration counter to time

        Parameters
        ----------
        itr : int
            iteration counter
            
        Returns
        -------
        time : str
            time in HH:MM format
    """

    start_hour = 7
    start_min = 0 

    current_hour = start_hour + min//60
    current_min = start_min + min%60

    if current_hour < 10:
        current_hour = '0{}'.format(current_hour)
    else:
        current_hour = '{}'.format(current_hour)
    
    if current_min < 10:
        current_min = '0{}'.format(current_min)
    else:
        current_min = '{}'.format(current_min)

    current_time = "{}:{}".format(current_hour, current_min)

    return current_time
