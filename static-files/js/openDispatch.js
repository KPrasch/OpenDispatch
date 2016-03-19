openDispatch = angular.module('openDispatch', []);

openDispatch.controller('incidentsController', function($scope, $http) {
    function updateMapMarkers() {
        if ($scope.incidents.length) {
            for(var i=0; i< $scope.incidents.length; i++) {
                $scope.incidents[i];
            }
        }
    }
    function getRecentIncidents(venueQuery) {
        venueQuery = venueQuery || '';
        if(venueQuery === '') {
            $http.get('http://localhost:8000/api/incidents')
                .then(function(response) {
                    $scope.incidents = response.data;

                    console.log(response);
                });
        } else {
            $http.get('http://localhost:8000/api/incidents/venue/' + venueQuery)
                .then(function (response) {
                    $scope.incidents = response.data;

                    console.log(response);
                });
        }
    }
    map.on('style.load', function() {
        getRecentIncidents();
    });
    $scope.$watch('searchIncidents', function(newValue, oldValue) {
        if(newValue !== oldValue) {
            getRecentIncidents($scope.searchIncidents);
        }
    });
    $scope.incidentPopUp = new mapboxgl.Popup({closeOnClick: false});
    $scope.showIncidentPopUp = function(incident) {

        var incidentPopUpHTML = '<ul class="incident-popup">' +
                                '   <li class="status"><span class="type crit">'+ incident.meta.dispatch +'</span></li>' +
                                '   <li>Address: '+ incident.meta.street_address +'</li>' +
                                '   <li>Dispatched at: '+ incident.dispatch_time +'</li>' +
                                //'   <li>'+ incident.location.streetview_url +'</li>' +
                                '</ul>';

        var incidentPopUp = $scope.incidentPopUp
            .setLngLat([incident.location.lng, incident.location.lat])
            .setHTML(incidentPopUpHTML)
            .addTo(map);

        map.flyTo({
            center: [incident.location.lng, incident.location.lat],
            zoom: 15.813832357478109,
            bearing: 0,

            speed: 3.5,
            curve: 1,

            easing: function(t) {
                return t;
            }
        });
    };
});
