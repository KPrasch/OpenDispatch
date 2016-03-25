$(function() {
  $('input#search-incidents').on({
    'focus': function(e) {
      $(this).addClass('focused');
    },
    'blur': function(e) {
      $(this).removeClass('focused');
    }
  });
  $('#toggle-incidents-view').click(function() {
    $('incident-reports').animate({
      width: 'toggle'
    }, {
      start: function() {
        map.invalidateSize();
      },
      step: function() {
        map.invalidateSize();
      },
      complete: function() {
        map.invalidateSize();
      },
      duration: 300
    });
  });
});
$('incident-reports').perfectScrollbar();
