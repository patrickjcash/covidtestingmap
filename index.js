let map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 11,
    center: new google.maps.LatLng(40.743, -73.953),
    mapTypeId: "terrain",
  });
  // Create a <script> tag and set the USGS. URL as the source.
  const script = document.createElement("script");
  // This example uses a local copy of the GeoJSON stored at
  // http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojsonp
  script.src =
    "cvmap.json";
  document.getElementsByTagName("head")[0].appendChild(script);
}

// Loop through the results array and place a marker for each
// set of coordinates.
const cvfeed_callback = function (results) {
  for (let i = 0; i < results.features.length; i++) {
    const coords = results.features[i].geometry.coordinates;
    const latLng = new google.maps.LatLng(coords[1], coords[0]);
    const name = results.features[i].properties.name;
    const detail = results.features[i].properties.detail;
    const color = results.features[i].properties.color;
    const wait = results.features[i].properties.wait;
    const reported = results.features[i].properties.reported;

    const infowindow = new google.maps.InfoWindow({
      content: detail + wait + reported,
    });
    const marker = new google.maps.Marker({
      position: latLng,
      map: map,
      title: name,
      animation: google.maps.Animation.DROP,
      icon: {                             
        url: "http://maps.google.com/mapfiles/ms/icons/" + color + "-dot.png",
        scaledSize: new google.maps.Size(36, 36),
      },
    });
    marker.addListener("click", () => {
     infowindow.open(map, marker);
    });
  }
}