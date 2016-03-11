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
    center: [-74.2585695256215, 41.8881456255846],
    zoom: 7.5,
    trackResize: true
  });
});
$(function() {
  $('incident-map').prepend('<div id="toggle-incidents-view">ll</div>');
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
