function clickButton(incident_id, realtime) {
    IncidentLayer.eachLayer(function(marker) {
        if (marker.feature.id == incident_id) {
            map.panTo(marker.getLatLng());
            marker.openPopup();
        }
        $("#dispatch-list>li.incident-li-active").removeClass("incident-li-active");
        $('li[data-incidentId='+incident_id+']').addClass('incident-li-active');
        if (realtime == "true") {

        }
    });
}

function RefreshMap(feature) {
    var incidentHTML = '<li class="incident-li" id="incident-li" onclick="clickButton('+feature.id+')" data-incidentId="'+feature.id+')">' +
    '<div class="meta-created">'+feature.properties.dispatch_time+'</div>' +
    '<div class="meta-dispatch">'+feature.properties.meta.dispatch+'</div>' +
    '<div class="meta-coords">lng:'+feature.properties.location.lat+ '|' +feature.properties.location.lng+'</div>' +
    '<div class="meta-venue">'+feature.properties.meta.venue+'</div>' +
    '<div class="meta-xsts">'+feature.properties.meta.intersection+'</div></li>';

     $(incidentHTML).prependTo($("#dispatch-list"));
     IncidentLayer.loadURL('/get_geoincidents/');
     clickButton(feature.id, "true");
}

var sock = new SockJS('/twitter-dispatches/incidents');

 sock.onopen = function(e) {
     sock.send(JSON.stringify({"hx_subscribe": "twitter-dispatches"}));
     console.log('ws:' + e.data);
 };

 sock.onmessage = function(e) {
     console.log('message', e.data);
     var dispatch_list = document.getElementById('dispatch-list');

     messageJSON = JSON.parse(e.data);

     if(messageJSON.hasOwnProperty('geometry')) {
         RefreshMap(messageJSON);
     } else {
        div = document.getElementById('notifier');
        div.innerHTML = div.innerHTML + JSON.stringify(messageJSON);
        function fade_out() {
          div.innerHTML = '';
        };
        setTimeout(fade_out, 10000);
     }

 };

 //sock.close();