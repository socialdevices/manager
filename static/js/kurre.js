// This is necessary in order to comply with Django's CSRF checks
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

$(document).ready(function() {
    connect(null);
});

function callComplete(response) {
    latest = response.latest;

    if (response.events.length > 0) {
        var at_bottom = null
        if ($(window).scrollTop() + $(window).height() == $(document).height()) {
            at_bottom = true;
        } else {
            at_bottom = false;
        }

        $.each(response.events, function() {
            var event_item = $('<li><span class="date">' + this.date + ' - </span><span class="description">' + this.msg + '</span></li>').hide().fadeIn('slow');
            $('ul#log').append(event_item);
        });

        if (at_bottom) {
            $('html, body').animate({
                scrollTop: $('ul#log li:last').offset().top
	        }, 2000);
        }
    }

    connect(latest);
};

function connect(seq_num) {
    $.post('events/', {latest: seq_num}, callComplete, 'json');
};
