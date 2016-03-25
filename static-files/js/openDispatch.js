hostUrl = 'localhost:8000/';
hostUrl = '//' + hostUrl;
openDispatch = angular.module('openDispatch', []);

openDispatch.controller('incidentsController', function($scope, $http) {
  function updateMapMarkers() {
    if ($scope.incidents.length) {
      for (var i = 0; i < $scope.incidents.length; i++) {
        $scope.incidents[i];
      }
    }
  }

  function getRecentIncidents(venueQuery) {
    venueQuery = venueQuery || '';
    if (venueQuery === '') {
      $http.get(hostUrl + 'api/incidents/')
        .then(function(response) {
          $scope.incidents = response.data;

          console.log(response);
        });
    } else {
      $http.get(hostUrl + 'api/incidents/venue/' + venueQuery)
        .then(function(response) {
          $scope.incidents = response.data;

          console.log(response);
        });
    }
  }
  incidentsLayer.on('ready', function() {
    getRecentIncidents();
  });
  $scope.$watch('searchIncidents', function(newValue, oldValue) {
    if (newValue !== oldValue) {
      getRecentIncidents($scope.searchIncidents);
    }
  });
  /*
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
          zoom: 13.813832357478109,
          bearing: 0,

          speed: 3.5,
          curve: 0.7,

          easing: function(t) {
              return t;
          }
      });
  };
  */
});
