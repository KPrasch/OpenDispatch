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
            "type": "symbol",
            "source": "incidents",
            "layout": {
                "icon-image": "marker-15"
            }
        });

        // Display the earthquake data in three layers, each filtered to a range of
        // count values. Each range gets a different fill color.
        var layers = [
            [150, '#f28cb1'],
            [20, '#f1f075'],
            [0, '#51bbd6']
        ];

        layers.forEach(function (layer, i) {
            map.addLayer({
                "id": "cluster-" + i,
                "type": "circle",
                "source": "incidents",
                "paint": {
                    "circle-color": layer[1],
                    "circle-radius": 12 / ( (i+1) * 0.25 )
                },
                "filter": i == 0 ?
                    [">=", "point_count", layer[0]] :
                    ["all",
                        [">=", "point_count", layer[0]],
                        ["<", "point_count", layers[i - 1][0]]]
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
