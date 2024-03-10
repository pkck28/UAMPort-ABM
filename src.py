# Classes for the model, vehicle, ports and hub
# Unit of analysis: minute or seconds

import matplotlib.pyplot as plt
import copy

class Vehicle():

    def __init__(self, id, location, max_energy, recharge_rate):

        self.id = id
        self.location = location
        self.max_energy = max_energy # units
        self.avail_energy = copy.deepcopy(max_energy) # units
        self.recharge_rate = recharge_rate # units/min
        self.status = 'ground'

class Hub():

    def __init__(self, location, hover_location, num_pads, turnaround_time):

        self.location = location
        self.hover_location = hover_location
        self.num_pads = num_pads
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

        # Instance variables
        self.hub = hub
        self.ports = ports
        self.vehicles = vehicles

        # Assigning the initial variables for the hub
        self.hub.avail_pads = self.hub.num_pads
        self.hub.takeoff = 0
        self.hub.land = 0
        self.hub.queue = []

        for port in self.ports:
            port.avail_pads = 0 # Since vehicles are occupying the pads
            port.takeoff = 0
            port.land = 0
            port.queue = []

        # Assigning the initial variables for the vehicles
        for vehicle in self.vehicles:
            vehicle.destination = None
            vehicle.wait_time = 0
            vehicle.status = 'ground'

    def run(self):
        """
            Method to run the simulation
        """

        # Simlulation loop
        for i in range(self.iterations):

            # Vehicle position updated asynchronusly
            for vehicle in self.vehicles:

                # Vehicle is flying towards destination
                if vehicle.status == 'flight' and vehicle.travel_time > 0:
                    vehicle.location[0] += vehicle.dx
                    vehicle.location[1] += vehicle.dy
                    vehicle.travel_time -= 1
                    vehicle.avail_energy -= 1

                # Vehicle has reached the destination's hover location
                elif vehicle.status == 'flight' and vehicle.travel_time == 0:
                    
                    if vehicle.id not in vehicle.destination.queue:
                            vehicle.destination.queue.append(vehicle.id)

                    # Land if a pad is available and next in queue or hover
                    if vehicle.destination.avail_pads > 0 and vehicle.id == vehicle.destination.queue[0]:
                        vehicle.location[0] = vehicle.destination.location[0]
                        vehicle.location[1] = vehicle.destination.location[1]
                        vehicle.avail_energy -= 1
                        vehicle.status = 'ground'
                        vehicle.wait_time = vehicle.destination.turnaround_time
                        vehicle.destination.land += 1
                        vehicle.destination.avail_pads -= 1
                        vehicle.destination.queue.remove(vehicle.id)
                    else:
                        vehicle.avail_energy -= 0.5

                # Vehicle is on the ground until turnaround time
                elif vehicle.status == 'ground' and vehicle.wait_time > 0:

                    vehicle.wait_time -= 1
                    
                    # Recharge the vehicle if it is at the hub
                    if isinstance(vehicle.destination, Hub) and vehicle.avail_energy < vehicle.max_energy:
                        vehicle.avail_energy += vehicle.recharge_rate

                # Vehicle is on the ground and ready to takeoff
                elif vehicle.status == 'ground' and vehicle.wait_time == 0:

                    # Only takeoff if vehicle has enough energy for round trip
                    if isinstance(vehicle.destination, Hub) and vehicle.avail_energy < 2.5*self.ports[vehicle.id].time_to_hub:
                            vehicle.avail_energy += vehicle.recharge_rate
                        
                    else:

                        # Setting next destination based on the current destination
                        if isinstance(vehicle.destination, Hub):
                            self.hub.takeoff += 1
                            self.hub.avail_pads += 1
                            vehicle.location[0] = self.hub.hover_location[vehicle.id,0]
                            vehicle.location[1] = self.hub.hover_location[vehicle.id,1]

                            vehicle.destination = self.ports[vehicle.id]
                            vehicle.travel_time = self.ports[vehicle.id].time_to_hub
                            vehicle.dx = (vehicle.destination.hover_location[0] - vehicle.location[0])/vehicle.travel_time
                            vehicle.dy = (vehicle.destination.hover_location[1] - vehicle.location[1])/vehicle.travel_time
                        else:
                            self.ports[vehicle.id].takeoff += 1
                            self.ports[vehicle.id].avail_pads += 1
                            vehicle.location[0] = self.ports[vehicle.id].hover_location[0]
                            vehicle.location[1] = self.ports[vehicle.id].hover_location[1]
                            
                            vehicle.destination = self.hub
                            vehicle.travel_time = self.ports[vehicle.id].time_to_hub
                            vehicle.dx = (vehicle.destination.hover_location[vehicle.id,0] - vehicle.location[0])/vehicle.travel_time
                            vehicle.dy = (vehicle.destination.hover_location[vehicle.id,1] - vehicle.location[1])/vehicle.travel_time

                        vehicle.status = 'flight'

            # Plotting
            self.plot(i)

    def plot(self, i=None):
        """
            Method to plot a single iteration in the simulation
        """

        color = ['r', 'b', 'g', 'm']
        port_radius = 0.15
        hub_radius = 0.3

        fig, ax = plt.subplots(figsize=(8, 8))

        # Plotting the hub
        circle = plt.Circle((self.hub.location[0], self.hub.location[1]), hub_radius, fill=False)
        ax.add_patch(circle)

        # Plotting the ports
        for index, port in enumerate(self.ports):
            circle = plt.Circle((port.location[0], port.location[1]), port_radius, fill=False)
            ax.add_patch(circle)
            ax.annotate(index+1, (port.location[0], port.location[1]), va="center", ha="center", fontsize=14)
            ax.plot(self.hub.hover_location[index,0], self.hub.hover_location[index,1], 'kx')
            ax.plot(port.hover_location[0], port.hover_location[1], 'kx')

        # Plotting the vehicles
        for index, vehicle in enumerate(self.vehicles):

            ax.quiver(vehicle.location[0], vehicle.location[1], vehicle.dx, vehicle.dy,
                        angles='xy', zorder=10, color=color[index], headlength=5, headwidth=4, 
                        headaxislength=5, pivot="middle", alpha=0.6, label=f'Vehicle {index+1}')

            # Annotate charge level
            ax.annotate(vehicle.avail_energy, (vehicle.location[0]+0.1, vehicle.location[1]+0.1), va="bottom", 
                        ha="left", fontsize=10)

        # Add no of takeoffs and landings
        data_loc = (self.hub.location[0]+2*hub_radius, self.hub.location[1]-2*hub_radius)
        ax.annotate(f'TO: {self.hub.takeoff}\nL: {self.hub.land}\n{self.hub.queue}', data_loc, va="center", ha="center", fontsize=12)

        # Asthetics
        if i is not None:
            ax.set_title(i)
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-2.6, 2.6)
        ax.legend(loc='upper left', fontsize=12)
        fig.tight_layout()
        plt.show()
        plt.close()
