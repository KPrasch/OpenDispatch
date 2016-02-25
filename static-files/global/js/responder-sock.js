
/*
var responderHTMML = '<li id="responder">' +
                     '<div id="responder-name">' + responder.name + '</div>' +
                     '<div id="responder-role">' + responder.role + '</div>' +
                     '<div id="responder-eta"' + responder.eta + '</div>' +
                     '<div id="responder-status">' + responder.status + '</div>' +
                     '</li>'
*/

var sock = new SockJS('/twilio-stream/responder-stream');

sock.onopen = function(e) {
 sock.send(JSON.stringify({"hx_subscribe": "twilio-stream"}));
 console.log('ws:' + e.data);
};

sock.onmessage = function(e) {
 console.log('message', e.data);
 var dispatch_list = document.getElementById('responder-list');

 messageJSON = JSON.parse(e.data);

 // Check for map data
 if(messageJSON.hasOwnProperty('geometry')) {
     RefreshMap(messageJSON);
 } else {

 }
 // In either case...
 $(responderHTML).prependTo($("#responder-list"));

};

$(function() {
    $.get('/get_recent_incidents/', function(data) {
        for(feature of data.features) {
            var incidentHTML = '<li class="incident-li" id="incident_'+feature.id+'" onclick="clickButton('+feature.id+')">' +
                '<div class="incident-close" id="close_'+feature.id+'">X</div>' +
                '<div class="meta-created">'+feature.properties.dispatch_time+'</div>' +
                '<div class="meta-dispatch">'+feature.properties.meta.dispatch+'</div>' +
                '<div class="meta-coords">lng:'+feature.properties.location.lat+ '|' +feature.properties.location.lng+'</div>' +
                '<div class="meta-venue">'+feature.properties.meta.venue+'</div>' +
                '<div class="meta-xsts">'+feature.properties.meta.intersection+'</div></li>';
            $(incidentHTML).prependTo($("#dispatch-list"));
        }
        $('.incident-close').click(function() {
            incident_id = $(this).attr('id').split('_')[1];
            $(this).hide(50, function() {
                $('#incident_'+incident_id).slideUp(100, function() {
                    $('#incident_'+incident_id).remove();
                    console.log($("#dispatch-list").children().length);
                    if($("#dispatch-list").children().length <= 0) {
                        $("#below-responders").fadeOut(200);
                    }
                });
            });
        });
    });

})();

