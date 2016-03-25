$(function() {
// Custom HTML tag setup
    var DateRangeSliderProto = Object.create(HTMLDivElement.prototype);
    var DateRangeSliderTag = document.registerElement('date-range-slider', {
        prototype:  DateRangeSliderProto
    });

    $dateRangeSlider = $('date-range-slider');
    $dateRangeSlider.append('<slider id="start"></slider><slider id="stop"></slider>');
    $('slider').append('<div class="slide-date-view"></div>');
    $sliders = $('slider');
    $startSlider = $('slider#start');
    $stopSlider = $('slider#stop');
    var startX = 0;
    var stopX = 1;
    var startDate = new Date(2016, 1, 20);
    var stopDate = new Date(2016, 2, 20);
    var startSliderDate = startDate;
    var stopSliderDate = stopDate;
    var range = stopDate.valueOf() - startDate.valueOf();

    $('#start .slide-date-view').text(startSliderDate.toLocaleDateString('en-US', {
        minute: 'numeric',
        hour: 'numeric',
        day : 'numeric',
        month : 'short',
        year : 'numeric'
    }).split(' ').join(' '));
    $('#stop .slide-date-view').text(stopSliderDate.toLocaleDateString('en-US', {
        minute: 'numeric',
        hour: 'numeric',
        day : 'numeric',
        month : 'short',
        year : 'numeric'
    }).split(' ').join(' '));

// https://stackoverflow.com/questions/11409895/whats-the-most-elegant-way-to-cap-a-number-to-a-segment
    Math.clamp = function(number, min, max) {
        return Math.max(min, Math.min(number, max));
    }

    if (!jQuery().draggable) {
        $.fn.draggable = function() {

            this
                .css('cursor', 'move')
                .on('mousedown touchstart', function(e) {
                    var $dragged = $(this);

                    var x = $dragged.offset().left - e.pageX,
                        y = $dragged.offset().top - e.pageY,
                        z = $dragged.css('z-index');

                    if (!$.fn.draggable.stack) {
                        $.fn.draggable.stack = 999;
                    }
                    stack = $.fn.draggable.stack;

                    $(window)
                        .on('mousemove.draggable touchmove.draggable', function(e) {

                            if($(e.target).is('.slide-date-view')) {
                                e.preventDefault();
                                return;
                            }

                            var scaledValue = Number(((x + e.pageX + 416) - 16.0) / ($('date-range-slider').width()+11.0 - 16.0)).toFixed(2);
                            if($(event.target).is('slider')) {
                                if($(event.target).attr('id') == 'start') startX = scaledValue;
                                if($(event.target).attr('id') == 'stop') stopX = scaledValue;
                            }

                            //console.log(scaledValue);

                            range = stopDate.valueOf() - startDate.valueOf();
                            startSliderDate = new Date(startX * (range) + startDate.valueOf());
                            stopSliderDate = new Date(stopX * (range) + startDate.valueOf());

                            if($(event.target).parents().has('slider')) {
                                if($(event.target).attr('id') == 'start') {
                                    $('#start .slide-date-view').text(startSliderDate.toLocaleDateString('en-US', {
                                        minute: 'numeric',
                                        hour: 'numeric',
                                        day : 'numeric',
                                        month : 'short',
                                        year : 'numeric'
                                    }).split(' ').join(' '));
                                }
                                if($(event.target).attr('id') == 'stop') {
                                    $('#stop .slide-date-view').text(stopSliderDate.toLocaleDateString('en-US', {
                                        minute: 'numeric',
                                        hour: 'numeric',
                                        day : 'numeric',
                                        month : 'short',
                                        year : 'numeric'
                                    }).split(' ').join(' '));
                                }
                            }

                            offsetX = Number(Math.clamp(x, 16, $('date-range-slider').width())).toFixed(0);

                            $dragged
                                .css({'z-index': stack, 'transform': 'scale(1.06)', 'transition': 'transform .3s', 'bottom': 'auto', 'right': 'auto'})
                                .offset({
                                    left: x
                                })
                                .find('a').one('click.draggable', function(e) {
                                e.preventDefault();
                            });

                            e.preventDefault();
                        })
                        .one('mouseup touchend touchcancel', function() {
                            $(this).off('mousemove.draggable touchmove.draggable click.draggable');
                            $dragged.css({'z-index': stack, 'transform': 'scale(1)'})
                            $.fn.draggable.stack++;
                        });

                    e.preventDefault();
                });
            return this;
        };
    }

// Maintain proper size
    $(window).resize(function(e) {
        $dateRangeSlider.animate({
            width: $dateRangeSlider.parent().width() - 32
        }, 0);
    });

// Make some nice divisions and indicate how long the daterange is
    var stepSize = 28/7;

// for-hell!
    for(var i=stepSize-1; i>=0; i--) {
        var medianDate = (i == stepSize-1) ? 1 : (1 / stepSize) * i;
        var dateRangeDivision = new Date(medianDate * (range) + startDate.valueOf());
        $dateRangeSlider.prepend('<span class="rangeDivision" style="width:'+100 / (stepSize) +'%;">'+dateRangeDivision.toLocaleDateString('en-US', {
                minute: 'numeric',
                hour: 'numeric',
                day : 'numeric',
                month : 'short',
                year : 'numeric'
            }).split(' ').join(' '));  +'</span>';
    }
// phew!

    $startSlider.draggable(); $stopSlider.draggable();
    $sliders.hover(function(e) {
        $sliders.find('.slide-date-view').show();
        $sliders.find('.slide-date-view').animate({
            opacity: 1,
        }, 200, function() {
            $('slider > *').clearQueue();
        });
    });
    $sliders.mouseup(function(e) {
        setTimeout(function() {
            $sliders.find('.slide-date-view').animate({
                opacity: 0
            }, 750, function() {
                $('slider > *').clearQueue();
                $(this).hide();
            });
        }, 2500);
    });

});