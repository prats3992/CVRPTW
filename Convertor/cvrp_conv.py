#! /usr/bin/env python3
import re

input_text = """
Objective: 150450
Route for vehicle 0:
Dtdc Courier Service Aerocity mohali Load(0) -> Sharon Resort Load(15) ->  Dtdc Courier Service Aerocity mohali (15)
Distance of the route: 19549m
Load of the route: 15

Route for vehicle 1:
Dtdc Courier Service Aerocity mohali Load(0) -> Jayant education Load(13) -> Akm Resorts Load(29) ->  Dtdc Courier Service Aerocity mohali (29)
Distance of the route: 18458m
Load of the route: 29

Route for vehicle 2:
Dtdc Courier Service Aerocity mohali Load(0) -> Radisson Hotel Chandigarh Zirakpur Load(10) ->  Dtdc Courier Service Aerocity mohali (10)
Distance of the route: 11564m
Load of the route: 10

Route for vehicle 3:
Dtdc Courier Service Aerocity mohali Load(0) -> Bestech Square Mall Load(12) -> The Mohali Club || Wyndham Chandigarh Mohali Load(24) ->  Dtdc Courier Service Aerocity mohali (24)
Distance of the route: 17399m
Load of the route: 24

Route for vehicle 4:
Dtdc Courier Service Aerocity mohali Load(0) -> Strawberry Global Smart School Load(14) -> The Amaltas Farms Load(25) ->  Dtdc Courier Service Aerocity mohali (25)
Distance of the route: 13914m
Load of the route: 25

Route for vehicle 5:
Dtdc Courier Service Aerocity mohali Load(0) -> Plaksha University Load(20) -> Singh Sheeda Gurdwara Sahib Load(40) ->  Dtdc Courier Service Aerocity mohali (40)
Distance of the route: 13652m
Load of the route: 40

Route for vehicle 6:
Dtdc Courier Service Aerocity mohali Load(0) -> Amity University, Mohali Load(18) ->  Dtdc Courier Service Aerocity mohali (18)
Distance of the route: 8747m
Load of the route: 18

Route for vehicle 7:
Dtdc Courier Service Aerocity mohali Load(0) -> Mahendra Chaudhary Zoological Park, Chhat Bir Zoo, Zirakpur Load(12) -> La Palacio Luxury Banquet & Lawns - Wedding Palace in Zirakpur Load(24) ->  Dtdc Courier Service Aerocity mohali (24)
Distance of the route: 16875m
Load of the route: 24

Route for vehicle 8:
Dtdc Courier Service Aerocity mohali Load(0) -> Mohali IT City Park Load(13) ->  Dtdc Courier Service Aerocity mohali (13)
Distance of the route: 8152m
Load of the route: 13

Route for vehicle 9:
Dtdc Courier Service Aerocity mohali Load(0) -> Gurdwara Dushat Daman Durali Load(12) -> JLPL Falcon View Load(27) ->  Dtdc Courier Service Aerocity mohali (27)
Distance of the route: 22140m
Load of the route: 27

Total distance of all routes: 150450m
Total load of all routes: 225
"""
# Extracting relevant information using regular expressions
routes_info = re.findall(
    r'Route for vehicle \d+:(.*?)Distance of the route: (\d+)', input_text, re.DOTALL)

# Converting to the desired format
converted_routes = []

for route in routes_info:
    start_end = re.findall(r'(\w[^->]*)', route[0].strip())
    start = start_end[0].strip().split('Load')[0].strip()
    end = start_end[-1].strip().split('Load')[0].strip()
    waypoints = [waypoint.strip().split('Load')[0].strip()
                 for waypoint in start_end[1:-1]] if len(start_end) > 2 else []
    converted_route = {
        'start': start,
        'end': end
    }

    if waypoints:
        converted_route['waypoints'] = waypoints

    converted_routes.append(converted_route)

with open('../Plotting/cvrp.js', 'w') as f:
    f.write('''function initMap() {\n
  const mapData = [\n''')
    for route in converted_routes:
        f.write(str(route).replace("'start'", "start").replace(
            "'end'", "end").replace("'waypoints'", "waypoints") + ',\n')
    f.write(''',
  ];

  for (let i = 0; i < mapData.length; i++) {
      const mapContainer = document.createElement("div");
          mapContainer.id = `map-${i}`;
      mapContainer.className = "map-container";
      document.getElementById("container").appendChild(mapContainer);
  
      const map = new google.maps.Map(mapContainer, {
        zoom: 13,
        center: { lat: 30.7052, lng: 76.785 },
      });
  
      const directionsService = new google.maps.DirectionsService();
      const directionsRenderer = new google.maps.DirectionsRenderer({ map });
      
      geocodeAddress(mapData[i].start, (startLocation) => {
        if (startLocation) {
          const startMarker = createCustomMarker(startLocation, "DEPOT");
          startMarker.setMap(map);
        } else {
          console.error("Unable to geocode start location:", mapData[i].start);
        }
  
        geocodeAddress(mapData[i].end, (endLocation) => {
          if (endLocation) {
            const endMarker = createCustomMarker(endLocation, "DEPOT");
            endMarker.setMap(map);
  
            // Calculate and display the route
      calculateAndDisplayRoute(
      mapData[i],
      directionsService,
            directionsRenderer,
        startLocation,
              endLocation
      );
    } else {
            console.error("Unable to geocode end location:", mapData[i].end);
          }
        });
      });
    }
  }
  
  function calculateAndDisplayRoute(
  mapData,
    directionsService,
    directionsRenderer,
    startLocation,
    endLocation
  ) {
    const waypts = mapData.waypoints.map((waypoint) => ({
      location: waypoint,
      stopover: true,
    }));
  
    directionsService
      .route({
        origin: startLocation,
        destination: endLocation,
        waypoints: waypts,
        optimizeWaypoints: true,
        travelMode: google.maps.TravelMode.DRIVING,
      })
      .then((response) => {
        directionsRenderer.setDirections(response);
  
        const route = response.routes[0];
        const summaryPanel = document.createElement("div");
        summaryPanel.className = "directions-panel";
        document.getElementById("container").appendChild(summaryPanel);
  
        if (mapData.waypoints.length) {
          summaryPanel.innerHTML = `<b>Route for Map ${mapData.start} to ${mapData.end} via ${mapData.waypoints}</b><br>`;
        } else {
          summaryPanel.innerHTML = `<b>Route for Map ${mapData.start} to ${mapData.end}</b><br>`;
        }
  
  // Manually add markers for waypoints
        for (let i = 0; i < route.legs.length - 1; i++) {
          const waypointLocation = route.legs[i].end_location;
          const waypointMarker = createCustomMarker(waypointLocation, "WAYPOINT");
          waypointMarker.setMap(directionsRenderer.getMap());
        }
  
        // Suppress default markers for start and end points
        directionsRenderer.suppressMarkers = true;
  
        for (let i = 0; i < route.legs.length; i++) {
      const routeSegment = i + 1;
  
          summaryPanel.innerHTML +=
            "<b>Route Segment: " + routeSegment + "</b><br>";
          summaryPanel.innerHTML += route.legs[i].start_address + " to ";
          summaryPanel.innerHTML += route.legs[i].end_address + "<br>";
          summaryPanel.innerHTML += route.legs[i].distance.text + "<br><br>";
        }
      })
      .catch((e) => window.alert("Directions request failed due to " + e));
  }
  function createCustomMarker(position, label) {
    return new google.maps.Marker({
      position: new google.maps.LatLng(position.lat, position.lng),
      label: {
        text: label,
        color: "BLACK", // Label text color
      },
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 10,
        fillColor: label === "WAYPOINT" ? "blue" : "pink", // Custom color for waypoints
        fillOpacity: 1,
        strokeWeight: 1,
        strokeColor: "white", // Set the stroke color
      },
      map: null, // Set map property to the map object when placing on the map
    });
  }
  
  function geocodeAddress(locationName, callback) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: locationName }, (results, status) => {
      if (status === "OK") {
        const location = results[0].geometry.location;
        callback({ lat: location.lat(), lng: location.lng() });
      } else {
        console.error(
          "Geocode was not successful for the following reason:",
          status
        );
        callback(null);
      }
    });
  }
  
  window.initMap = initMap;''')
