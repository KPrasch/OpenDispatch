

var responderHTMML = '<li id="responder">' +
                     '<div id="responder-name">' + responder.name + '</div>' +
                     '<div id="responder-role">' + responder.role + '</div>' +
                     '<div id="responder-eta"' + responder.eta + '</div>' +
                     '<div id="responder-status">' + responder.status + '</div>' +
                     '</li>'

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

//sock.close();

