#! /usr/bin/env python3
import requests
import json
import urllib.request as urllib
import os
# The distances are in meters, and the times are in seconds in the matrices
LOCATION={
    0: 'Dtdc Courier Service Aerocity mohali',
    1: 'Mahendra Chaudhary Zoological Park, Chhat Bir Zoo, Zirakpur',
    2: 'Radisson Hotel Chandigarh Zirakpur',
    3: 'Plaksha University',
    4: 'Bestech Square Mall',
    5: 'JLPL Falcon View',
    6: 'Mohali IT City Park',
    7: 'Amity University, Mohali',
    8: 'Sharon Resort',
    9: 'La Palacio Luxury Banquet & Lawns - Wedding Palace in Zirakpur',
    10: 'Strawberry Global Smart School',
    11: 'Akm Resorts',
    12: 'Gurdwara Dushat Daman Durali',
    13: 'Jayant education',
    14: 'The Mohali Club || Wyndham Chandigarh Mohali',
    15: "The Amaltas Farms",
    16: 'Singh Sheeda Gurdwara Sahib'
}

def create_data():
    """Creates the data for route distances and times."""
    data = {}
    with open("API_KEY_HOLDER.env") as f:
        x = f.readline()
    data['API_key'] = x.strip()
    data['locations'] = [r'Dtdc+Courier+Service+Aerocity+mohali',  # depot
                         r'Mahendra+Chaudhary+Zoological+Park,+Chhat+Bir+Zoo,+Zirakpur',
                         r'Radisson+Hotel+Chandigarh+Zirakpur',
                         r'Plaksha+University',
                         r'Bestech+Square+Mall',
                         r'JLPL+Falcon+View',
                         r'Mohali+IT+City+Park',
                         r'Amity+University,+Mohali',
                         r'Sharon+Resort',
                         r'La+Palacio+Luxury+Banquet+%26+Lawns+-+Wedding+Palace+in+Zirakpur',
                         r'Strawberry+Global+Smart+School',
                         r'Akm+Resorts',
                         r'Gurdwara+Dushat+Daman+Durali',
                         r'Jayant+education',
                         r'The+Mohali+Club+%7C%7C+Wyndham+Chandigarh+Mohali',
                         r"The+Amaltas+Farms",
                         r'Singh+Sheeda+Gurdwara+Sahib']
    return data


def get_route_distances(data):
    API_key = data["API_key"]
    locations = data['locations']
    num_locations = len(locations)
    distance_matrix = []

    for origin in locations:
        row_distances = []
        for destination in locations:
            if origin == destination:
                # No need to calculate distance to the same location
                row_distances.append(0)
            else:
                response = send_request(origin, destination, API_key)
                distance = extract_route_distance(response)
                row_distances.append(distance)
        distance_matrix.append(row_distances)

    return distance_matrix


def get_route_times(data):
    API_key = data["API_key"]
    locations = data['locations']
    num_locations = len(locations)
    time_matrix = []

    for origin in locations:
        row_times = []
        for destination in locations:
            if origin == destination:
                # No need to calculate time to the same location
                row_times.append(0)
            else:
                response = send_request(origin, destination, API_key)
                duration = extract_route_duration(response)
                row_times.append(duration)
        time_matrix.append(row_times)

    return time_matrix


def send_request(origin, destination, API_key):
    """ Build and send request for the given origin and destination addresses."""
    request = 'https://maps.googleapis.com/maps/api/directions/json?'
    request += f'origin={origin}&destination={destination}&key={API_key}&units=metric'
    jsonResult = urllib.urlopen(request).read()
    response = json.loads(jsonResult)
    return response


def extract_route_distance(response):
    if 'routes' in response and len(response['routes']) > 0:
        route = response['routes'][0]
        if 'legs' in route and len(route['legs']) > 0:
            leg = route['legs'][0]
            if 'distance' in leg and 'value' in leg['distance']:
                return leg['distance']['value']

    return None

def max_val(file: str) -> int:
    with open(file) as f:
        matrix = [[int(num) for num in line.split("\t")] for line in f]
    return max(max(row) for row in matrix)


def extract_route_duration(response):
    if 'routes' in response and len(response['routes']) > 0:
        route = response['routes'][0]
        if 'legs' in route and len(route['legs']) > 0:
            leg = route['legs'][0]
            if 'duration' in leg and 'value' in leg['duration']:
                return leg['duration']['value']

    return None


def main():
    data = create_data()

    # Get and print the route distance matrix
    distance_matrix = get_route_distances(data)
    print("Route Distance Matrix:")
    for row_distances in distance_matrix:
        print(row_distances)

    # Get and print the route time matrix
    time_matrix = get_route_times(data)
    print("\nRoute Time Matrix:")
    for row_times in time_matrix:
        print(row_times)

    # Save the matrices to text files
    with open("distance_matrix.txt", "w") as f:
        for row_distances in distance_matrix:
            f.write("\t".join(str(d) for d in row_distances) + "\n")

    with open("time_matrix.txt", "w") as f:
        for row_times in time_matrix:
            f.write("\t".join(str(t) for t in row_times) + "\n")


if __name__ == '__main__':
    main()
