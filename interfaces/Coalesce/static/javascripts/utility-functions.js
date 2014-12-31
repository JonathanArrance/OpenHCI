// ---------------- //
// MESSAGE HANDLING
// ---------------- //

var message = new message_handle();


// ---------------- //
// CONSOLE ACTIONS
// ---------------- //

var instanceConsoleLinks = {
    add: function (id, link) {
        instanceConsoleLinks[id] = link;
    },
    get: function (id) {
        return instanceConsoleLinks[id];
    }
};

$(document).on('click', '.open-instance-console', function () {

    // Prevent scrolling to top of page on click
    event.preventDefault();

    // Open dialog window to contain iFrame
    $("#instance-console-dialog").dialog({
        autoOpen: false,
        height: 482,
        width: 763,
        modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position: {
            my: "center",
            at: "center",
            of: $('#page-content')
        },
        close: function () {
        }
    });

    // Set iFrame src to instance console link
    $("#instance-console-frame").attr("src", instanceConsoleLinks.get($(this).parent().parent().attr("id")));

    // Refresh the frame
    $('#instance-console-frame').attr('src', function (i, val) {
        return val;
    });

    $("#instance-console-dialog").dialog("open");
});

$(document).on('click', '#refresh-console', function () {

    $('.widget-console').attr('src', function (i, val) {
        return val;
    });
});


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


// ---------------- //
// GUID
// ---------------- //

function S4() {
    // Generate a random number string for use in a guid.
    return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
}

function guid() {
    // Generate a guid without the dashes.
    return (S4() + S4() + S4() + "4" + S4().substr(0, 3) + S4() + S4() + S4() + S4()).toLowerCase();
}


// ---------------- //
// URL MANIPULATION
// ---------------- //

function convertUrl47(url) {
    // Convert a URL from having /s to %47.
    for (var i = 0; i < url.length; i++) {
        if (url[i] == '/') {
            url = url.substr(0, i) + "%47" + url.substr(i, url.length + 1);
            i = i + 2;
        }
    }
    return url;
}


// ---------------- //
// UI VALIDATION
// ---------------- //

function flagError(input, t) {
    input.before('<div class="error">' + t + '</div>');
    $('error').addClass("ui-state-highlight").fadeIn();
    setTimeout(function () {
        $('error').removeClass("ui-state-highlight", 1500);
    }, 500);
}

function checkLength(o, n, min, max) {
    if (o.val().length > max || o.val().length < min) {
        o.addClass("ui-state-error");
        flagError(o, n + " must be between " + min + " and " + max + ".");
        return false;
    } else {
        return true;
    }
}

function checkRegexp(o, regexp, n) {
    if (!( regexp.test(o.val()))) {
        o.addClass("ui-state-error");
        flagError(o, n);
        return false;
    } else {
        return true;
    }
}

function checkUsername(o) {
    var regexp = /^[a-z]([0-9a-z_])+$/i;
    if (!( regexp.test(o.val()))) {
        o.addClass("ui-state-error");
        flagError(
            o,
            "Username may consist of a-z, 0-9 and underscores, and must being with a letter.");
        return false;
    } else {
        return true
    }
}

function checkEmail(o) {
    var regexp = /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i;
    if (!( regexp.test(o.val()))) {
        o.addClass("ui-state-error");
        flagError(
            o,
            "Email must formatted as: 'user@domain.com'.");
        return false;
    } else {
        return true
    }
}

function checkPassword(o) {
    var regexp = /^([0-9a-zA-Z])+$/;
    if (!( regexp.test(o.val()))) {
        o.addClass("ui-state-error");
        flagError(
            o,
            "Password may consist of a-z and 0-9.");
        return false;
    } else {
        return true
    }
}

function checkPasswordMatch(p, c) {
    if (p.val() != c.val()) {
        p.addClass("ui-state-error");
        c.addClass("ui-state-error");
        flagError(
            c,
            "Passwords do not match.");
        return false;
    } else {
        return true;
    }
}

function checkStorage(o) {
    if (o.val() > availableStorage) {
        o.addClass("ui-state-error");
        flagError(
            o,
                "There is only " + availableStorage + "gbs of available storage.");
        return false;
    } else {
        return true;
    }
}

function checkUrl(url) {
    var urlregex = new RegExp("^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*$");
    if (urlregex.test(url.val())) {
        return (true);
    }
    url.addClass("ui-state-error");
    flagError(
        url,
        "Invalid remote URL.");
    return (false);
}

function checkFile(file) {
    if (file.val() == '') {
        flagError(
            file,
            "A local file must be selected.");
        return false;
    } else {
        return true;
    }
}

function checkDuplicateName(name, hashTable) {
    var pass = true;
    for (item in hashTable.items) {
        var i = hashTable.getItem(item);
        if (name.val() == i.option) {
            pass = false;
        }
    }

    if (!pass) {
        flagError(
            name,
            "Name is already in use.");
    }

    return pass;
}

function clearUiValidation(fields) {
    fields.removeClass("ui-state-error");
    $('.error').each(function () {
        $(this).fadeOut().remove();
    });
}

function resetUiValidation(fields) {
    fields.val("").removeClass("ui-state-error");
    $('.error').each(function () {
        $(this).fadeOut().remove();
    });
}


// ---------------- //
// DOM MANIPULATION
// ---------------- //

// --- GENERAL

function HashTable() {
    this.length = 0;
    this.items = [];

    for (var i = 0; i < arguments.length; i += 2) {
        if (typeof (arguments[i + 1]) != 'undefined') {
            this.items[arguments[i]] = arguments[i + 1];
            this.length++;
        }
    }

    this.removeItem = function (in_key) {
        var tmp_previous;
        if (typeof (this.items[in_key]) != 'undefined') {
            this.length--;
            tmp_previous = this.items[in_key];
            delete this.items[in_key];
        }

        return tmp_previous;
    };

    this.getItem = function (in_key) {
        return this.items[in_key];
    };

    this.setItem = function (in_key, in_value) {
        var tmp_previous;
        if (typeof (in_value) != 'undefined') {
            if (typeof (this.items[in_key]) == 'undefined') {
                this.length++;
            } else {
                tmp_previous = this.items[in_key];
            }

            this.items[in_key] = in_value;
        }

        return tmp_previous;
    };

    this.hasItem = function (in_key) {
        return typeof (this.items[in_key]) != 'undefined';
    };

    this.clear = function () {
        for (var i in this.items) {
            delete this.items[i];
        }

        this.length = 0;
    }
}

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

var disabledProgressbars = {
    instances: 0, images: 0, fips: 0,
    volumes: 0, snapshots: 0, containers: 0,
    extNets: 0, routers: 0, privateNets: 0,
    users: 0, secGroups: 0, keys: 0
};

function disableProgressbar(id, widget, bool) {
    if (bool) {
        disabledProgressbars[widget]--;

        if (disabledProgressbars[widget] <= 0) {
            if ($(id).is(":visible")) {
                $(id).fadeOut('fast');
                disabledProgressbars[widget] = 0;
            }
        }
    } else {
        if ($(id).is(":hidden")) {
            $(id).fadeIn('fast');
        }

        disabledProgressbars[widget]++;
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

    var actions = '.' + id;
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

function disableFormInputs(id, inputTypes, bool) {
    for (var i = 0; i < inputTypes.length; i++) {
        var type = '.' + id + '-' + inputTypes[i];
        $(type).each(function () {
            $(this).prop("disabled", bool);
        });
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

function refreshSelect(select, hashTable) {
    $(select).empty();
    for (var item in hashTable.items) {
        var i = hashTable.getItem(item);
        $(select).append(
                '<option value="' + i.value + '">' + i.option + '</option>'
        );
    }
}

function removeFromSelect(value, select, hashTable) {
    hashTable.removeItem(value);
    refreshSelect(select, hashTable);
}

function addToSelect(value, option, select, hashTable) {
    hashTable.setItem(value, { value: value, option: option });
    refreshSelect(select, hashTable);
}
// --- INSTANCE MANAGEMENT

var instances = new HashTable(),
    images = new HashTable(),
    assignableFips = new HashTable(),
    assignableInstances = new HashTable();

// --- STORAGE

var totalStorage = 0,
    usedStorage = 0,
    availableStorage = 0,
    attachableInstances = new HashTable();

function getUsedStorage(rows) {

    usedStorage = 0;

    $(rows).each(function () {
        if (isNaN(parseInt($(this).attr("class")))) {
        } else {
            usedStorage += parseInt($(this).attr("class"));
        }
    });

    availableStorage = totalStorage - usedStorage;
}

// --- SOFTWARE DEFINED NETWORKS

var privateNetworks = new HashTable();

// --- USERS/SECURITY

var securityGroups = new HashTable(),
    securityKeys = new HashTable();

// --- UNASSIGNED USERS

var unassignedUsers = 0;

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

