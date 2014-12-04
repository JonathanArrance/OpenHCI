// --- MESSAGE HANDLING

var message = new message_handle();

// --- UI VALIDATION

function updateTips(tips, t) {
    tips.append('<div class="error">' + t + '</div>').addClass("ui-state-highlight").fadeIn();
    setTimeout(function () {
        tips.removeClass("ui-state-highlight", 1500);
    }, 500).fadeOut();
}

function checkLength(tips, o, n, min, max) {
    if (o.val().length > max || o.val().length < min) {
        o.addClass("ui-state-error");
        updateTips(tips, "Length of " + n + " must be between " + min + " and " + max + ".");
        return false;
    } else {
        return true;
    }
}

function checkRegexp(tips, o, regexp, n) {
    if (!( regexp.test(o.val()) )) {
        o.addClass("ui-state-error");
        updateTips(tips, n);
        return false;
    } else {
        return true;
    }
}

// --- DOM MANIPULATION

var disabledLinks = 0;

function disableLinks(bool){

    var links = '.disable-link';
    var activeColor = '#AD682B';
    var disabledColor = '#696969';

    if (bool) {
        $(links).bind('click', false);
        $(links).css('color', disabledColor);
        disabledLinks++;
    } else {
        disabledLinks--;

        if (disabledLinks <=0) {
            $(links).unbind('click', false);
            $(links).css('color', activeColor);
            disabledLinks = 0;
        }
    }
}

function disableActions(id, bool) {

    var actions = '.'+id+'-disable-action';
    var activeColor = '#AD682B';
    var disabledColor = '#696969';

    if (bool) {
        $(actions).bind('click', false);
        $(actions).css('color', disabledColor);
    } else {
        $(actions).unbind('click', false);
        $(actions).css('color', activeColor);
    }
}

function setVisible(selector, bool){
    if (bool){
        if ($(selector).is(":hidden")) {
            $(selector).fadeIn();
        }
    } else {
        if ($(selector).is(":visible")) {
            $(selector).fadeOut();
        }
    }
}

// --- CSRF

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}