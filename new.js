function initMap() {
  const directionsService = new google.maps.DirectionsService();
  const directionsRenderer = new google.maps.DirectionsRenderer();
  const maps = document.querySelectorAll(".map");

  maps.forEach((mapElement) => {
    const map = new google.maps.Map(mapElement, {
      zoom: 6,
      center: { lat: 41.85, lng: -87.65 },
    });

    directionsRenderer.setMap(map);

    mapElement.nextElementSibling.addEventListener("click", () => {
      calculateAndDisplayRoute(
        directionsService,
        directionsRenderer,
        mapElement
      );
    });
  });
}

function calculateAndDisplayRoute(
  directionsService,
  directionsRenderer,
  mapElement
) {
  const waypts = [];
  const checkboxArray = mapElement.parentElement.querySelector(".waypoints");

  for (let i = 0; i < checkboxArray.length; i++) {
    if (checkboxArray.options[i].selected) {
      waypts.push({
        location: checkboxArray[i].value,
        stopover: true,
      });
    }
  }

  directionsService
    .route({
      origin: mapElement.parentElement.querySelector(".start").value,
      destination: mapElement.parentElement.querySelector(".end").value,
      waypoints: waypts,
      optimizeWaypoints: true,
      travelMode: google.maps.TravelMode.DRIVING,
    })
    .then((response) => {
      directionsRenderer.setDirections(response);

      const route = response.routes[0];
      const summaryPanel = mapElement.nextElementSibling.nextElementSibling;

      summaryPanel.innerHTML = "";

      // For each route, display summary information.
      for (let i = 0; i < route.legs.length; i++) {
        const routeSegment = i + 1;

        summaryPanel.innerHTML +=
          "<b>Route Segment: " + routeSegment + "</b><br>";
        summaryPanel.innerHTML += route.legs[i].start_address + " to ";
        summaryPanel.innerHTML += route.legs[i].end_address + "<br>";
        summaryPanel.innerHTML += route.legs[i].distance.text + "<br><br>";
      }
    })
    .catch((e) => window.alert("Directions request failed due to " + status));
}

window.initMap = initMap;
