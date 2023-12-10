#! /usr/bin/env python3
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
from route_matrices import LOCATION


# Storing all data into one data model - the function below returns set of all data points combined
def create_data_model():
    data = {}
    with open("time_matrix.txt", "r") as f:
        data["time_matrix"] = [
            [int(num) for num in line.split("\t")] for line in f.readlines()]
    data["time_windows"] = [
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
    with open("distance_matrix.txt", "r") as f:
        data["distance_matrix"] = [
            [int(num) for num in line.split("\t")] for line in f.readlines()]
    data['demandLB'] = [0, 12, 10, 20, 12, 15, 13,
                        18, 15, 12, 14, 16, 12, 13, 12, 11, 20]
    data['vehicle_capacitiesLB'] = [15, 35, 10, 25, 25, 40, 25, 25, 20, 30]
    data['depot'] = 0
    return data

# function to print the results/solution


def print_solution(data, manager, routing, solution):
    print(f'Objective: {solution.ObjectiveValue()}')  # the objective function
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    total_distance = 0
    total_loadLB = 0
    total_loadM3 = 0
    for vehicle_id in range(len(data['vehicle_capacitiesLB'])):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        loading_output = 'Load for vehicle {}:'.format(vehicle_id)
        route_distance = 0
        route_loadLB = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2}) -> '.format(
                manager.IndexToNode(index), solution.Min(time_var), solution.Max(time_var))
            index = solution.Value(routing.NextVar(index))
            node_index = manager.IndexToNode(index)
            route_loadLB += data['demandLB'][node_index]
            loading_output += ' {0} Load({1}) -> '.format(node_index,
                                                          route_loadLB)
            previous_index = index
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                    solution.Min(time_var),
                                                    solution.Max(time_var))
        plan_output += 'Time of the route: {}min\n'.format(
            solution.Min(time_var))
        plan_output += 'Distance of the route: {}m'.format(route_distance)
        loading_output += 'Load of the route: {}'.format(route_loadLB)
        print(plan_output)
        print(loading_output)
        total_distance += route_distance
        total_loadLB += route_loadLB
        total_time += solution.Min(time_var)
    print('Total time of all routes: {}min'.format(total_time))
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_loadLB))

# Defining main() function


def main():
    data = create_data_model()
    # Create node index to variable index mapping
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),                                    len(
        data['vehicle_capacitiesLB']), data['depot'])
    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
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
        400,  # allow waiting time (min)
        2500,  # maximum time (min) per vehicle in a route (8 hours)
        False,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)

    # Add time window constraints for each location except depot - (one can define time window constraints for depot as well by small modifications in below code)
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    depot_idx = data['depot']
    for vehicle_id in range(len(data['vehicle_capacitiesLB'])):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot_idx][0],
            data['time_windows'][depot_idx][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(len(data['vehicle_capacitiesLB'])):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Add Capacity Weight constraint.
    def demand_callbackLB(from_index):
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demandLB'][from_node]
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callbackLB)

    # Add Vehicle capacity weight Contraint
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacitiesLB'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.seconds = 50
    search_parameters.solution_limit = 100**3
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)


if __name__ == '__main__':
    main()
