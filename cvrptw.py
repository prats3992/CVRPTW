#! /usr/bin/env python3
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Named constants
ALLOWABLE_WAITING_TIME = 400
MAXIMUM_TIME_PER_VEHICLE = 2500


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


def define_routing_model(data, manager):
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        ALLOWABLE_WAITING_TIME,
        MAXIMUM_TIME_PER_VEHICLE,
        False,
        time)
    time_dimension = routing.GetDimensionOrDie(time)

    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    depot_idx = data['depot']
    for vehicle_id in range(len(data['vehicle_capacitiesLB'])):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot_idx][0],
            data['time_windows'][depot_idx][1])

    for i in range(len(data['vehicle_capacitiesLB'])):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    def demand_callbackLB(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demandLB'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callbackLB)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data['vehicle_capacitiesLB'],
        True,
        'Capacity')

    return routing


def print_solution(data, manager, routing, solution):
    print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    total_distance = 0
    total_loadLB = 0

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


def main():
    data = create_data_model()
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           len(data['vehicle_capacitiesLB']),
                                           data['depot'])
    routing = define_routing_model(data, manager)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.solution_limit = 1000**3
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("No solution found.")

if __name__ == '__main__':
    main()
