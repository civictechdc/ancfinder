function initialize_google_map(with_controls) {
  // Create a basic roadmap centered on Washington, DC.

  try {
    google;
  } catch (err) {
    return; // We're working off-line and don't have access to Google Maps.
  }
  
  google.maps.visualRefresh = true;

  var myOptions = {
    zoom: 4,
    center: new google.maps.LatLng(38, -96),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    panControl: with_controls,
    zoomControl: with_controls,
    zoomControlOptions: {
      style: google.maps.ZoomControlStyle.SMALL
    },
    mapTypeControl: with_controls,
    scaleControl: with_controls,
    streetViewControl: false,
    styles: [ { "featureType": "poi.park", "elementType": "geometry.fill", "stylers": [ { "visibility": "off" } ] } ]
    };
  map = new google.maps.Map(document.getElementById("map_canvas_google"), myOptions);
  
  map.fitBounds(new google.maps.LatLngBounds(
    new google.maps.LatLng(38.869472385, -77.1014200414),
    new google.maps.LatLng(38.9613165232, -76.923349042)));
  
  map.overlayMapTypes.clear();
}

// Add a tile overlay for this layer.
function add_overlay(map, layer, minzoom, maxzoom, opacity) {
  if (!opacity) opacity = 1.0;
  var tileimgformat = 'png';
  if (navigator.appName == 'Microsoft Internet Explorer' && new RegExp("MSIE [678]").exec(navigator.userAgent)) tileimgformat = 'gif';
  
  var overlay = new google.maps.ImageMapType({
    getTileUrl: function(coord, zoom) {
      if (maxzoom && zoom > maxzoom) return null; // minZoom, maxZoom ineffectual below?
      if (minzoom && zoom < minzoom) return null;
      return "http://gis.govtrack.us/map/tiles/" + layer + "/" + zoom + "/" + coord.x + "/" + coord.y + "." + tileimgformat + "?gen=8";
    },
    tileSize: new google.maps.Size(256, 256),
    isPng: tileimgformat == 'png',
    
    minZoom: minzoom,
    maxZoom: maxzoom,
    opacity: (tileimgformat == 'png' ? .8 : .25) * opacity
  });
  map.overlayMapTypes.insertAt(0, overlay);
}