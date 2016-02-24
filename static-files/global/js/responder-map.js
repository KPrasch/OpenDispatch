
$(function() {
	var $loading = $('#loader').hide();
	$(document)
	.ajaxStart(function () {
		$loading.show();
	})
	.ajaxStop(function () {
		$loading.hide();
	});
	return false;
});

// Zack did this.
$(".nano").nanoScroller({ alwaysVisible: true });

L.mapbox.accessToken = 'pk.eyJ1Ijoia3ByYXNjaCIsImEiOiJ0U1RtQVpvIn0.wHmPex20_XUmpjL2a0a4mQ';
mapboxgl.accessToken = 'pk.eyJ1Ijoia3ByYXNjaCIsImEiOiJ0U1RtQVpvIn0.wHmPex20_XUmpjL2a0a4mQ';


if (!mapboxgl.supported()) {
    alert('Your browser does not support Mapbox GL');

} else {
    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/kprasch/cikh63zrs004j9vkooy90by64',
        center: [ -74.2600, 41.8900],
        zoom: 9
    });
}


var map = L.mapbox.map('responder-map', null, {minZoom: 9, maxZoom:22})
              .setView([41.8900, -74.2600], 10);

var layers = document.getElementById('menu-ui');

var IncidentLayer = new L.mapbox.featureLayer().loadURL(geoJSON);

//var MostRecentLayer = new L.mapbox.featureLayer()
//    .loadURL('https://wanderdrone.appspot.com/')
    // Once this layer loads, we set a timer to load it again in a few seconds.
//    .on('ready', run_recent)
//    .addTo(map);

addLayer(IncidentLayer, 'Incidents (all)', 1, "false");
addLayer(L.mapbox.tileLayer('mapbox.streets'), 'Streets', 4, "false");
addLayer(L.mapbox.tileLayer('mapbox.satellite'), 'Satellite', 5, "false");
addLayer(L.mapbox.tileLayer('mapbox.outdoors'), 'Outdoors', 6, "true");



function addLayer(layer, name, zIndex, initial) {
    // Create a simple layer switcher that
    // toggles layers on and off.
    var link = document.createElement('a');
        link.href = '#';
        link.className = '';
        link.innerHTML = name;

        if (initial == "true") {
        layer.setZIndex(zIndex)
        layer.addTo(map);
        link.className = 'active';
        } else {
        layer.setZIndex(zIndex);
        }

    link.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (map.hasLayer(layer)) {
            map.removeLayer(layer);
            this.className = '';
        } else {
            map.addLayer(layer);
            this.className = 'active';
        }
    };

    layers.appendChild(link);
}


IncidentLayer.on('layeradd', function(e) {
  var marker = e.layer,
  feature = marker.feature;
  marker.setIcon(L.icon({"iconUrl": "/static/img/RedDot.svg",
                         "iconSize": [9, 9],
                         "iconAnchor": [0, 0],
                         "popupAnchor": [4, 0],
                         "className": "dot"}));

  // Create custom popup content
  var popupContent =  '<div class="incident-tooltip">' +
                       feature.properties.meta.dispatch + " in " + feature.properties.meta.location +
                       '<ul class="tooltip-list">' +
                       '<li>' + feature.properties.meta.street_address + ', {{ locale_state }}</li>' +
                       '<li>' + feature.properties.meta.intersection + '</li>' +
                       '<li> Lng: ' + feature.properties.location.lng + '</li>' +
                       '<li> Lat: ' + feature.properties.location.lat + '</li>' +
                       '<li>Dispatched: ' + feature.properties.dispatch_time + '</li>' +
                       '<li>Twitter Received: ' + feature.properties.received_time + '</li>' +
                       '<li>Web Created: ' + feature.properties.created_time + '</li>' +
                       '<li>' + feature.id + '</li>' +
                       '<li><a href="/flag_incorrect/">Report an incorrect location.</a></li>' +
                       '<li><img class="streetview-img" src="' + feature.properties.location.streetview_url + '"></li>'
                       '</ul></div>';

  // http://leafletjs.com/reference.html#popup
  marker.bindPopup(popupContent,{
                   closeButton: true,
                   keepInView: true,
                   minWidth: 320
                   }).on('click', function(e) {
      list_id = e.target.feature.id;
      $("#dispatch-list>li.incident-li-active").removeClass("incident-li-active");

      $('li[data-incidentId='+list_id+']').addClass('incident-li-active');
      $(".nano").nanoScroller({ scrollTo:  $('li[data-incidentId='+list_id+']') });

    });
});


IncidentLayer.on('ready', function() {
    // featureLayer.getBounds() returns the corners of the furthest-out markers,
    // and map.fitBounds() makes sure that the map contains these.

});
