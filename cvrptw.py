#! /usr/bin/env python3
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import route_matrices as rm

# Data Inputs: Next step is to import the data of ‘Demands’, ‘Time windows’, ‘Vehicle capacities’, ‘Distance matrix’ and ‘Time matrix’. Once done we will create a data model combining all the data points as shown below:

# demand_kg = import demand in kgs ('Customers', 'Demand(kg)')
# time_windows = import opening and closing hours of Hub and customers ('Site', 'OpenHours', 'CloseHours') - Format 1300 for 01:00 PM, 0000 for 12:00 AM and so on (the code accepts only Int)
# vehicle_capacities_kg = import vehicle capacities in kgs ('Vehicle','Capacity(kg)') - user can define multiple vehicles of same capacity as multiple entries and vice versa
# distanceMatrix = import distance matrix that includes hub and customers
# TimeMatrix = import time matrix based on average speed of a vehicle - it should be in sync with the time windows format (hour to hour and minutes to minutes)
# Storing all data into one data model - the function below returns set of all data points combined


def create_data_model():
    data = {}
    data_holder = rm.create_data()
    # TimeMatrix https://developers.google.com/optimization/routing/vrp#distance_matrix_api
    data['time_matrix'] = rm.get_route_times(data_holder)
    data['time_windows'] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]  # time_windows
    # distanceMatrix https://developers.google.com/optimization/routing/vrp#distance_matrix_api
    data['distance_matrix'] = rm.get_route_distances(data_holder)
    data['demand_kg'] = [0, 1, 1, 2, 4, 2, 4, 8,
                         8, 1, 2, 1, 2, 4, 4, 8, 8]  # demand_kg
    data['vehicle_capacities_kg'] = [15, 15, 15, 15]  # vehicle_capacities_kg
    data['depot'] = 0
    data["num_vehicles"] = 4
    return data


def print_solution(data, manager, routing, solution):
    print(f'Objective: {solution.ObjectiveValue()}')  # the objective function
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    total_distance = 0
    total_loadLB = 0
    total_loadM3 = 0
    for vehicle_id in range(len(data['vehicle_capacities_kg'])):
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
            route_loadLB += data['demand_kg'][node_index]
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


def main():
    data = create_data_model()
    print(data['time_matrix'])
    print(data['time_windows'])
    print(data['distance_matrix'])
    print(data['demand_kg'])
    print(data['vehicle_capacities_kg'])
    print(data['depot'])
    print(data["num_vehicles"])
    # Create node index to variable index mapping
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),                                    len(
        data['vehicle_capacities_kg']), data['depot'])
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
        120,  # allow waiting time (min)
        900,  # maximum time (min) per vehicle in a route (8 hours)
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
    for vehicle_id in range(len(data['vehicle_capacities_kg'])):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot_idx][0],
            data['time_windows'][depot_idx][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(len(data['vehicle_capacities_kg'])):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Add Capacity Weight constraint.
    def demand_callbackLB(from_index):
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demand_kg'][from_node]
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callbackLB)

    # Add Vehicle capacity weight Contraint
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities_kg'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    print(solution)
    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    ...


if __name__ == '__main__':
    main()
