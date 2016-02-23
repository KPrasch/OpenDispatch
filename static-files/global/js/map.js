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


$(function() {
	$("#list-filter-input").autocomplete({
		minLength: 0,
		disabled: false,
		source: function( request, response ) {
			$.ajax({
				type:"GET",
				url: "/incidents/search/",
				dataType: "json",
				data: {term:request.term},
				close: function () {

				},
				success: function (data) {
					IncidentLayer.setGeoJSON(data);
					 map.fitBounds(IncidentLayer.getBounds(), {paddingTopLeft: [-400, -800]});
				}
			});
		}
	});
});

// Zack did this.
$(".nano").nanoScroller({ alwaysVisible: true });


$( "#slider" ).mouseup(function() {
  var dateSliderBounds = $("#slider").dateRangeSlider("values");
  var min = dateSliderBounds.min.toJSON();
  var max = dateSliderBounds.max.toJSON();

    $.ajax({
        type: "GET",
        url: "/incidents/filter/daterange/",
        dataType: "json",
        data: {min:min, max:max},
        close: function () {

        },
        success: function (data) {
        IncidentLayer.setGeoJSON(data);
        //map.fitBounds(IncidentLayer.getBounds());
        }
    });

});


$( "#minimize-lower-panes" ).toggle(function() {

  $( "#lower-panes-container" ).animate({
      bottom: "-=300px"
  }, 500, function() {
      $(this).css("display", "none");

  });

}, function() {
    $( "#lower-panes-container" ).animate({
      display: "toggle",
      bottom: "+=300px"
    }, 500);
});


var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"];
  $("#slider").dateRangeSlider({
    bounds: {min: new Date(2016, 0, 1), max: new Date(2016, 11, 31, 12, 59, 59)},
    defaultValues: {min: new Date(2016, 0, 1), max: new Date()},
    scales: [{
      first: function(value){ return value; },
      end: function(value) {return value; },
      next: function(value){
        var next = new Date(value);
        return new Date(next.setMonth(value.getMonth() + 1));
      },
      label: function(value){
        return months[value.getMonth()];
      },
      format: function(tickContainer, tickStart, tickEnd){
        tickContainer.addClass("myCustomClass");
      }
    }]
  });


L.mapbox.accessToken = 'pk.eyJ1Ijoia3ByYXNjaCIsImEiOiJ0U1RtQVpvIn0.wHmPex20_XUmpjL2a0a4mQ';
mapboxgl.accessToken = 'pk.eyJ1Ijoia3ByYXNjaCIsImEiOiJ0U1RtQVpvIn0.wHmPex20_XUmpjL2a0a4mQ';

/*
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
*/

var map = L.mapbox.map('map', null, {minZoom: 9, maxZoom:22})
              .setView([41.8900, -74.2600], 10);

var layers = document.getElementById('menu-ui');

// geoJSON defined with inline scrip iun the template to us template tags
var IncidentLayer = new L.mapbox.featureLayer().loadURL(geoJSON);
var ClusterLayer = new L.MarkerClusterGroup();

//var MostRecentLayer = new L.mapbox.featureLayer()
//    .loadURL('https://wanderdrone.appspot.com/')
    // Once this layer loads, we set a timer to load it again in a few seconds.
//    .on('ready', run_recent)
//    .addTo(map);

//var heat = L.heatLayer([geojson], { maxZoom: 12 });

addLayer(IncidentLayer, 'Incidents (all)', 1, "false");
addLayer(ClusterLayer, 'Incidents (cluster)', 2, "true");
//addLayer(heat, 'Heat Map', 3, false);
addLayer(L.mapbox.tileLayer('mapbox.streets'), 'Streets', 4, "false");
addLayer(L.mapbox.tileLayer('mapbox.satellite'), 'Satellite', 5, "false");
addLayer(L.mapbox.tileLayer('mapbox.outdoors'), 'Outdoors', 6, "true");
addLayer(L.mapbox.tileLayer('kprasch.59f9f541'), 'Civil Borders', 7, "false");


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
    ClusterLayer.addLayer(IncidentLayer);

});


//var runLayer = omnivore.kml('/static/product/data/ulster-agencies.kml')
//    .on('ready', function() {
//        map.fitBounds(runLayer.getBounds());
//    })
//    .addTo(map);

