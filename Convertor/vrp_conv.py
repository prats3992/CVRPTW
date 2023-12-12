#! /usr/bin/env python3
import re

input_text = """Objective: 2057090
Route for vehicle 0:
Dtdc Courier Service Aerocity mohali -> Mohali IT City Park -> Dtdc Courier Service Aerocity mohali
Distance of the route: 8152m

Route for vehicle 1:
Dtdc Courier Service Aerocity mohali -> Mahendra Chaudhary Zoological Park, Chhat Bir Zoo, Zirakpur -> Radisson Hotel Chandigarh Zirakpur -> Akm Resorts -> Dtdc Courier Service Aerocity mohali
Distance of the route: 18904m

Route for vehicle 2:
Dtdc Courier Service Aerocity mohali -> Dtdc Courier Service Aerocity mohali
Distance of the route: 0m

Route for vehicle 3:
Dtdc Courier Service Aerocity mohali -> Dtdc Courier Service Aerocity mohali
Distance of the route: 0m

Route for vehicle 4:
Dtdc Courier Service Aerocity mohali -> Bestech Square Mall -> The Mohali Club || Wyndham Chandigarh Mohali -> JLPL Falcon View -> Dtdc Courier Service Aerocity mohali
Distance of the route: 18195m

Route for vehicle 5:
Dtdc Courier Service Aerocity mohali -> La Palacio Luxury Banquet & Lawns - Wedding Palace in Zirakpur -> Sharon Resort -> Dtdc Courier Service Aerocity mohali
Distance of the route: 19549m

Route for vehicle 6:
Dtdc Courier Service Aerocity mohali -> Strawberry Global Smart School -> Jayant education -> The Amaltas Farms -> Dtdc Courier Service Aerocity mohali
Distance of the route: 18857m

Route for vehicle 7:
Dtdc Courier Service Aerocity mohali -> Plaksha University -> Gurdwara Dushat Daman Durali -> Singh Sheeda Gurdwara Sahib -> Amity University, Mohali -> Dtdc Courier Service Aerocity mohali
Distance of the route: 18533m

Maximum of the route distances: 19549m"""

# Extracting relevant information using regular expressions
routes_info = re.findall(
    r'Route for vehicle \d+:(.*?)Distance of the route: (\d+)m', input_text, re.DOTALL)

# Converting to the desired format
converted_routes = []

for route in routes_info:
    start_end = route[0].strip().split('->')
    start = start_end[0].strip()
    end = start_end[-1].strip()
    waypoints = [waypoint.strip() for waypoint in start_end[1:-1]
                 ] if len(start_end) > 2 else []

    converted_route = {
        'start': start,
        'end': end
    }

    if waypoints:
        converted_route['waypoints'] = waypoints

    converted_routes.append(converted_route)

# Printing the result
with open('../Plotting/vrp.js', 'w') as f:
    f.write('''function initMap() {\n
  const mapData = [\n''')
    for route in converted_routes:
        f.write(str(route).replace("'start'","start").replace("'end'","end").replace("'waypoints'","waypoints") + ',\n')
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
