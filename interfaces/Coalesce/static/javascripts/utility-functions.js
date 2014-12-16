// ---------------- //
// MESSAGE HANDLING
// ---------------- //

var message = new message_handle();



// ---------------- //
// CONSOLE ACTIONS
// ---------------- //

$(document).on('click', '#refresh-console', function () {
    $('.widget-console').attr('src', function (i, val) {
        return val;
    });
});



// ---------------- //
// UI VALIDATION
// ---------------- //

function updateTips(tips, t) {
    tips.append('<div class="error">' + t + '</div>').addClass("ui-state-highlight").fadeIn();
    setTimeout(function () {
        tips.removeClass("ui-state-highlight", 1500);
    }, 500);
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

function checkStorage(tips, o) {
    if (o.val() > availableStorage) {
        o.addClass("ui-state-error");
        updateTips(tips, "There is only " + availableStorage + "gbs of available storage.");
        return false;
    } else {
        return true;
    }
}



// ---------------- //
// DOM MANIPULATION
// ---------------- //

// --- GENERAL

var disabledLinks = 0;

function disableLinks(bool) {

    var links = '.disable-link';
    var activeColor = '#AD682B';
    var disabledColor = '#696969';


    if (bool) {
        if (disabledLinks <= 0) {
            $(links).addClass('disabled-link');
            $(links).css('color', disabledColor);
        }

        disabledLinks++;
    } else {
        disabledLinks--;

        if (disabledLinks <= 0) {
            $(links).removeClass('disabled-link');
            $(links).css('color', activeColor);
            disabledLinks = 0;
        }
    }
}

function disableLink(id, bool) {

    var activeColor = '#AD682B';
    var disabledColor = '#696969';

    if (bool) {
        $(id).addClass('disabled-link');
        $(id).css('color', disabledColor);
    } else {
        $(id).removeClass('disabled-link');
        $(id).css('color', activeColor);
    }
}

function disableActions(id, bool) {

    var actions = '.' + id + '-disable-action';
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

function disableUiButtons(id, bool) {
    if (bool) {
        $(id).attr('disabled', true);
        $(id).css('cursor', 'inherit');
    } else {
        $(id).attr('disabled', false);
        $(id).css('cursor', 'pointer');
    }
}

function setVisible(selector, bool) {
    if (bool) {
        if ($(selector).is(":hidden")) {
            $(selector).fadeIn('fast');
        }
    } else {
        if ($(selector).is(":visible")) {
            $(selector).fadeOut('fast');
        }
    }
}

function emptyAndAppend(selector, newContent) {
    fadeOutAndEmpty(selector);
    setTimeout(function () {
        appendAndFadeIn(selector, newContent);
    }, 500);
}

function fadeOutAndEmpty(selector) {
    setVisible(selector, false);
    $(selector).empty();
}

function appendAndFadeIn(selector, newContent) {
    $(selector).append(newContent);
    setVisible(selector, true);
}

// --- VOLUME STORAGE

var totalStorage = 0;
var usedStorage = 0;
var availableStorage = 0;

function getUsedStorage(rows) {

    usedStorage = 0;

    $(rows).each(function () {

        if (isNaN(parseInt($(this).attr("class")))) {
        } else {
            usedStorage += parseInt($(this).attr("class"));
        }
    });

    availableStorage = totalStorage - usedStorage;
    console.log(totalStorage + ' - ' + usedStorage + ' = ' + availableStorage);
}

// --- FLOATING IPs

// --- BUG FIXER: Add <div id="delete-check></div> before TEXT NODES needing to be deleted on page load
function deleteCheck(containerId) {
    $(document).ready(function () {
        var textNodes = $(containerId).contents()
            .filter(function () {
                return this.nodeType === 3;
            });

        textNodes.each(function () {
            if (this.previousSibling == document.getElementById("delete-check")) {
                $(this).remove();
            }
        });
    });
}




// ---------------- //
// CSRF
// ---------------- //

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

