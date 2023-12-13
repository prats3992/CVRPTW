function initMap() {
  const mapData = [
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: ["Strawberry Global Smart School"],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: [
        "Bestech Square Mall",
        "The Mohali Club || Wyndham Chandigarh Mohali",
      ],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: ["JLPL Falcon View"],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: ["Akm Resorts", "Jayant education"],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: [
        "Plaksha University",
        "Singh Sheeda Gurdwara Sahib",
        "Gurdwara Dushat Daman Durali",
      ],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: ["Amity University, Mohali"],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: ["The Amaltas Farms", "Radisson Hotel Chandigarh Zirakpur"],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: ["Mohali IT City Park"],
    },
    {
      start: "Dtdc Courier Service Aerocity mohali",
      end: "Dtdc Courier Service Aerocity mohali",
      waypoints: [
        "La Palacio Luxury Banquet & Lawns",
        "Wedding Palace in Zirakpur",
        "Mahendra Chaudhary Zoological Park, Chhat Bir Zoo, Zirakpur",
        "Sharon Resort",
      ],
    },
  ];

  for (let i = 0; i < mapData.length; i++) {
    const mapAndPanelContainer = document.createElement("div");
    mapAndPanelContainer.className = "map-and-panel-container";
    document.getElementById("container").appendChild(mapAndPanelContainer);

    // Create map container
    const mapContainer = document.createElement("div");
    mapContainer.id = `map-${i}`;
    mapContainer.className = "map-container";
    mapAndPanelContainer.appendChild(mapContainer);

    // Create directions panel container
    const directionsPanelContainer = document.createElement("div");
    directionsPanelContainer.className = "directions-panel";
    mapAndPanelContainer.appendChild(directionsPanelContainer);

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
            endLocation,
            directionsPanelContainer
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
  endLocation,
  directionsPanelContainer
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
      directionsPanelContainer.appendChild(summaryPanel);

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
      color: "black", // Label text color
    },
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 20,
      fillColor: label === "WAYPOINT" ? "blue" : "#ffdb00", // Custom color for waypoints
      fillOpacity: 1,
      strokeWeight: 1,
      strokeColor: "black", // Set the stroke color
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

window.initMap = initMap;
