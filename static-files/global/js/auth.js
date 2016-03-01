active = "add-location-form";
$(document).ready(function() {
    $("#add-location-form-container").modal({
      escapeClose: true,
      clickClose: true,
      showClose: false
    });
});
$(function() {
    $("#login-form").on("submit", function(event) {
        preventDefault();
        $.ajax({
            type: "POST",

        });
    });

    $("#add-location-form-progress > a").click(function(event) {
        if (active == event.target.id) {
            return;
        }

        wasClicked = "#add-"+event.target.id.split("-")[1]+"-form";
        removeActive = "#show-"+active.split("-")[1]+"-form";

        console.log(wasClicked);
        console.log(removeActive);

        $("#"+active).css('display', 'none').promise().done(function() {
            $(removeActive).removeClass('active');
            $(wasClicked).show();
            $("#"+event.target.id).addClass('active');
        });

        active = wasClicked.replace('#', '');
    });
});