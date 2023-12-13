import re

input_text = """
Objective: 16144
Route for vehicle 0:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> La Palacio Luxury Banquet & Lawns - Wedding Palace in Zirakpur Time(447,447) Load(4) -> Mahendra Chaudhary Zoological Park, Chhat Bir Zoo, Zirakpur Time(878,878) Load(8) -> Sharon Resort Time(1263,1263) Load(16) -> Dtdc Courier Service Aerocity mohali Time(2271,2271) Load(16)
Time of the route: 2271min
Load of the route: 16

Route for vehicle 1:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Mohali IT City Park Time(850,850) Load(3) -> Dtdc Courier Service Aerocity mohali Time(1468,1468) Load(3)
Time of the route: 1468min
Load of the route: 3

Route for vehicle 2:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Akm Resorts Time(627,627) Load(1) -> Jayant education Time(1196,1196) Load(4) -> Dtdc Courier Service Aerocity mohali Time(2334,2334) Load(4)
Time of the route: 2334min
Load of the route: 4

Route for vehicle 3:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Plaksha University Time(533,533) Load(9) -> Singh Sheeda Gurdwara Sahib Time(996,996) Load(11) -> Gurdwara Dushat Daman Durali Time(1319,1319) Load(17) -> Dtdc Courier Service Aerocity mohali Time(2471,2471) Load(17)
Time of the route: 2471min
Load of the route: 17

Route for vehicle 4:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> The Amaltas Farms Time(526,659) Load(7) -> Radisson Hotel Chandigarh Zirakpur Time(1000,1000) Load(12) -> Dtdc Courier Service Aerocity mohali Time(1704,1704) Load(12)
Time of the route: 1704min
Load of the route: 12

Route for vehicle 5:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Amity University, Mohali Time(533,533) Load(3) -> Dtdc Courier Service Aerocity mohali Time(1345,1345) Load(3)
Time of the route: 1345min
Load of the route: 3

Route for vehicle 6:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Strawberry Global Smart School Time(816,816) Load(8) -> Dtdc Courier Service Aerocity mohali Time(1637,1637) Load(8)
Time of the route: 1637min
Load of the route: 8

Route for vehicle 7:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> JLPL Falcon View Time(697,697) Load(5) -> Dtdc Courier Service Aerocity mohali Time(1354,1354) Load(5)
Time of the route: 1354min
Load of the route: 5

Route for vehicle 8:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Dtdc Courier Service Aerocity mohali Time(0,0) Load(0)
Time of the route: 0min
Load of the route: 0

Route for vehicle 9:
Dtdc Courier Service Aerocity mohali Time(0,0) Load(0) -> Bestech Square Mall Time(850,850) Load(5) -> The Mohali Club || Wyndham Chandigarh Mohali Time(1141,1141) Load(7) -> Dtdc Courier Service Aerocity mohali Time(2173,2173) Load(7)
Time of the route: 2173min
Load of the route: 7

Total time of all routes: 16757min
"""

# Extracting relevant information using regular expressions
routes_info = re.findall(r'Route for vehicle \d+:(.*?)Time of the route: (\d+)min\nLoad of the route: (\d+)', input_text, re.DOTALL)

# Converting to the desired format
converted_routes = []

for route in routes_info:
    start_end = re.findall(r'(\w[^->]*)', route[0].strip())
    start = start_end[0].strip()
    end = start_end[-1].strip()
    waypoints = [waypoint.strip() for waypoint in start_end[1:-1]] if len(start_end) > 2 else []
    load = int(route[2])

    converted_route = {
        'start': start,
        'end': end,
        'load': load
    }

    if waypoints:
        converted_route['waypoints'] = waypoints

    converted_routes.append(converted_route)


with open('../Plotting/cvrptw.js', 'w') as f:
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
