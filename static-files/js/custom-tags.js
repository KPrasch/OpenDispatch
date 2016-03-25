//
// <app-container>
//
var AppContainerProto = Object.create(HTMLDivElement.prototype);
var AppContainerTag = document.registerElement('app-container', {
  protoype: AppContainerProto
});
//
// </app-container>
//

//
// <map-container>
//
var MapContainerProto = Object.create(HTMLDivElement.prototype);
var MapContainerTag = document.registerElement('map-container', {
  protoype: MapContainerProto
});
//
// </map-container>
//

//
// <incident-map>
//
var IncidentMapProto = Object.create(HTMLDivElement.prototype);
IncidentMapProto.createdCallback = function() {
  this.id = 'incident-map-view';
};
var IncidentMapTag = document.registerElement('incident-map', {
  prototype: IncidentMapProto
});

$(function() {
  L.mapbox.accessToken =
    'pk.eyJ1IjoiemFja2tvbGxhciIsImEiOiJjaWxjcWw5aG0zZmcydHVseGI3NWRqYno4In0.HO_q5jmiFLtRnG71hOqG4w';
  map = L.mapbox.map('incident-map-view', 'mapbox.streets')
    .setView(new L.LatLng(41.89001042401825, -74.22500610351561), 10);

  incidentsLayer = L.mapbox.featureLayer()
    .loadURL('http://localhost:8000/api/incidents/geo/')
    .addTo(map);
});

// ------------------------------------------------------------------ //

/*
$(function() {
  mapboxgl.accessToken =
    'pk.eyJ1IjoiemFja2tvbGxhciIsImEiOiJjaWxjcWw5aG0zZmcydHVseGI3NWRqYno4In0.HO_q5jmiFLtRnG71hOqG4w';

  map = new mapboxgl.Map({
    container: 'incident-map-view',
    style: 'mapbox://styles/zackkollar/cilih2w2500bc9pkvxeiv54mv',
    center: [-74.16567075875092, 41.865629817916016],

    zoom: 9.563293778598588,
    trackResize: true
  });


  map.on('style.load', function() {
    map.addSource('incidents', {
      type: 'geojson',
      data: 'http://localhost:8000/api/incidents/geo/',
      cluster: true,
      clusterRadius: 35,
      clusterMaxZoom: 14
    });

    map.addLayer({
      "id": "non-cluster-markers",
      "type": "circle",
      "source": "incidents",
      "paint": {
        "circle-color": '#BB0000',
        "circle-radius": 3
      }
    });

    // Display the earthquake data in three layers, each filtered to a range of
    // count values. Each range gets a different fill color.
    var layers = [
      [150, '#f28cb1'],
      [20, '#f1f075'],
      [2, '#71aaba']
    ];

    layers.forEach(function(layer, i) {
      map.addLayer({
        "id": "cluster-" + i,
        "type": "circle",
        "source": "incidents",
        "paint": {
          "circle-color": layer[1],
          "circle-radius": 10 / ((i + 1) * 0.25)
        },
        "filter": i == 0 ? [">=", "point_count", layer[0]] : [
          "all", [">=", "point_count", layer[0]],
          ["<", "point_count", layers[i - 1][0]]
        ]
      });
    });

    map.on('click', function(e) {
      console.log('she succ me')
      map.featuresAt(e.point, {
        layers: ['non-cluster-markers', 'cluster-0',
          'cluster-1', 'cluster-2'
        ],
        radius: 5,
        includeGeometry: true
      }, function(err, features) {
        console.log(features);
        if (err) throw err;
        // if there are features within the given radius of the click event,
        // fly to the location of the click events
        if (features.geometry.coordinates.length) {
          // Get coordinates from the symbol and center the map on those coordinates
          map.flyTo({
            center: features[0].geometry.coordinates[0][0]
          });
        }
      });
    });
    map.on('mousemove', function(e) {
      map.featuresAt(e.point, {
        layers: ['non-cluster-markers', 'cluster-0',
          'cluster-1', 'cluster-2'
        ],
        radius: 0.02
      }, function(err, features) {
        if (err) throw err;
        map.getCanvas().style.cursor = features.length ?
          'pointer' : '';
      });
    });

    // Add a layer for the clusters' count labels
    map.addLayer({
      "id": "cluster-count",
      "type": "symbol",
      "source": "incidents",
      "layout": {
        "text-field": "{point_count}",
        "text-font": [
          "DIN Offc Pro Medium",
          "Arial Unicode MS Bold"
        ],
        "text-size": 11
      }
    });

  });
});
*/



// ------------------------------------------------------------------ //


$(function() {
  $('incident-map').prepend("<div id='toggle-incidents-view'>ll</div>");
});
//
// </incident-map>
//

//
// <incident-reports>
//
var IncidentReportsProto = Object.create(HTMLDivElement.prototype);
var IncidentReportsTag = document.registerElement('incident-reports', {
  protoype: IncidentReportsProto
});
//
// </incident-reports>
//

//
// <incident-report>
//
var IncidentReportProto = Object.create(HTMLDivElement.prototype);
var IncidentReportTag = document.registerElement('incident-report', {
  protoype: IncidentReportProto
});
//
// </incident-report>
//

//
// <no-incidents>
//
var NoIncidentsProto = Object.create(HTMLDivElement.prototype);
var NoIncidentsTag = document.registerElement('no-incidents', {
  protoype: NoIncidentsProto
});
//
// </no-incidents>
//
