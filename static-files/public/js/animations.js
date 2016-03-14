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
        map.resize();
      },
      step: function() {
        map.resize();
      },
      complete: function() {
        map.resize();
      },
      duration: 300
    });
  });
});
