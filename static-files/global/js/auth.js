active = "add-location-form";
map = null;

$(function() {

    $("#sign-up").click(function(event) {
        $("#login-form").hide();
        $("#registration-form").show();
    });
    $("#back-to-login").click(function(event) {
        $("#registration-form").hide();
        $("#login-form").show();
    });


    $("#login-form").on("submit", function(event) {
        event.preventDefault();

        $.ajax({
            type: "POST",
            data: {
                username: $("input#username-input").val(),
                password: $("input#password-input").val()
            },
            success: function(data) {
                if (data.error != undefined) {
                    $(".errors").remove();
                    $('#login-container').prepend($('<div class="errors">'+ data.error +'</div>'));
                }
            }
        });
    });

    $("#registration-form #submit").click(function() {
        var formData = {
            username: $("input#id_username").val(),
            phone_number: $("input#id_phone_number").val(),
            citizen_notifications: '',
            email: $("input#id_email").val(),
            password: $("input#id_password").val(),
            first_name: $("input#id_first_name").val(),
            last_name: $("input#id_last_name").val(),
        }
        console.log(formData);
        $.ajax({
            type: "POST",
            url: "/api/accounts/",
            data: formData
        });
    });

    $("#add-location-form-progress > a, #add-location-form button").click(function(event) {
        if (active == event.target.id) {
            return;
        }

        wasClicked = "#add-"+event.target.id.split("-")[1]+"-form";
        removeActive = "#show-"+active.split("-")[1]+"-form";

        console.log(wasClicked);
        console.log(removeActive);

        $("#"+active).css('display', 'none').promise().done(function() {

            $("#add-location-form-container").modal({
                escapeClose: true,
                clickClose: true,
                showClose: false
            });

            $(removeActive).removeClass('active');
            $(wasClicked).show();
            $("#"+event.target.id).addClass('active');

            if(event.target.id.split("-")[1] == 'fixedpoint' && map == null) {
                L.mapbox.accessToken = 'pk.eyJ1Ijoia3ByYXNjaCIsImEiOiJ0U1RtQVpvIn0.wHmPex20_XUmpjL2a0a4mQ';
                map = L.mapbox.map('fixedpoint-form-map', 'mapbox.streets')
                    .setView([41.8900, -74.2600], 10)
                    .addControl(L.mapbox.geocoderControl('mapbox.places', {
                      keepOpen: true
                 }));

                var featureGroup = L.featureGroup().addTo(map);

                var drawControl = new L.Control.Draw({
                    edit: {
                        featureGroup: featureGroup
                    },
                    draw: {
                        polyline: false,
                        polygon: false,
                        rectangle: false,
                        circle: false
                    }
                }).addTo(map);

                map.on('draw:created', function(e) {
                    featureGroup.addLayer(e.layer);
                });
            }
        });

        active = wasClicked.replace('#', '');
    });
});