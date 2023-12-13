#! /usr/bin/env python
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from route_matrices import LOCATION

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    with open("time_matrix.txt", "r") as f:
        data["time_matrix"] = [
            [int(num) for num in line.split("\t")] for line in f.readlines()]
    data['time_windows'] = [
        (0, 600),   # depot
        (800, 1100),  # 1
        (1000, 1300),  # 2
        (400, 750),   # 3
        (850, 1200),  # 4
        (600, 1000),  # 5
        (850, 1100),  # 6
        (500, 900),   # 7
        (1200, 1400),  # 8
        (400, 800),   # 9
        (550, 850),   # 10
        (150, 1000),  # 11
        (600, 1500),  # 12
        (700, 1200),  # 13
        (900, 1300),  # 14
        (250, 700),   # 15
        (400, 1000),  # 16
    ]
    data['demands'] = [0, 4, 5, 9, 5, 5, 3,
                       3, 8, 4, 8, 1, 6, 3, 2, 7, 2]   # weights/demands for each node
    data['vehicle_capacities'] = [20, 20, 5, 20, 20, 20, 10, 20, 20, 20]
    data['num_vehicles'] = 10
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_load = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += '{0} Time({1},{2}) Load({3}) -> '.format(
                LOCATION[node_index], solution.Min(time_var),
                solution.Max(time_var), route_load)
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        node_index = manager.IndexToNode(index)
        route_load += data['demands'][node_index]
        plan_output += '{0} Time({1},{2}) Load({3})\n'.format(LOCATION[node_index],
                                                              solution.Min(
                                                                  time_var),
                                                              solution.Max(
                                                                  time_var),
                                                              route_load)
        plan_output += 'Time of the route: {}min\n'.format(
            solution.Min(time_var))
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_time += solution.Min(time_var)
    print('Total time of all routes: {}min'.format(total_time))


"""Solve the VRP with time windows."""
# Instantiate the data problem.
data = create_data_model()
# Create the routing index manager
# The inputs to RoutingIndexManager are:
#   The number of locations (including the depot)
#   The number of vehicles in the problem
#   The node corresponding to the depot

manager = pywrapcp.RoutingIndexManager(
    len(data['time_matrix']), data['num_vehicles'], data['depot'])
# Create Routing Model.
routing = pywrapcp.RoutingModel(manager)
# Create and register a transit callback.


def time_callback(from_index, to_index):
    """Returns the travel time between the two nodes."""
    # Convert from routing variable Index to time matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['time_matrix'][from_node][to_node]


transit_callback_index = routing.RegisterTransitCallback(time_callback)
# Define cost of each arc.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
# Add Time Windows constraint.
time = 'Time'
routing.AddDimension(
    transit_callback_index,
    1500,  # allow waiting time (1440 as it means the whole day in minutes)
    2500,  # maximum time per vehicle (all times are assumed to be in minutes)
    False,  # Don't force start cumul to zero.
    time)
time_dimension = routing.GetDimensionOrDie(time)
# Add time window constraints for each location except depot.
for location_idx, time_window in enumerate(data['time_windows']):
    if location_idx == data['depot']:
        continue
    index = manager.NodeToIndex(location_idx)
    time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
# Add time window constraints for each vehicle start node.
depot_idx = data['depot']
for vehicle_id in range(data['num_vehicles']):
    index = routing.Start(vehicle_id)
    time_dimension.CumulVar(index).SetRange(
        data['time_windows'][depot_idx][0],
        data['time_windows'][depot_idx][1])
# Instantiate route start and end times to produce feasible times.
for i in range(data['num_vehicles']):
    routing.AddVariableMinimizedByFinalizer(
        time_dimension.CumulVar(routing.Start(i)))
    routing.AddVariableMinimizedByFinalizer(
        time_dimension.CumulVar(routing.End(i)))
# Add Capacity constraint.


def demand_callback(from_index):
    """Returns the demand of the node."""
    # Convert from routing variable Index to demands NodeIndex.
    from_node = manager.IndexToNode(from_index)
    return data['demands'][from_node]


demand_callback_index = routing.RegisterUnaryTransitCallback(
    demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,  # null capacity slack
    data['vehicle_capacities'],  # vehicle maximum capacities
    True,  # start cumul to zero
    'Capacity')
# Setting first solution heuristic.
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
# Solve the problem.
solution = routing.SolveWithParameters(search_parameters)
# Print solution on console.
if solution:
    print_solution(data, manager, routing, solution)
else:
    print("No solution found !")
