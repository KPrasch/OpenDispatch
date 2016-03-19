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
        console.log("Getting incidents with q='"+venueQuery+"'!");
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
            //map.layers.forEach(function (value, i) {
            //   map.setFilter('cluster-'+i, ['in', 'meta.street_address', $scope.searchIncidents])
            //});
        }
    });
});
