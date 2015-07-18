$(function () {
    initializeUtilities();
});

function initializeUtilities() {
    // Call click events
    $(document).on('click', '#confirm', function (event) {
        event.preventDefault();
        var call = $(this).data("call"),
            notice = $(this).data("notice"),
            async = $(this).data("async"),
            buttons = $(this).parent().parent().find('button'),
            load = $.Deferred();
        showMessage('info', notice);
        setModalButtons(false, buttons);
        load = $.getJSON(call)
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                }
                if (data.status == 'success') {
                    showMessage('success', data.message);
                    closeModal();
                }
            })
            .fail(function () {
                showMessage('error', 'Server Fault');
            })
            .always(function () {
                setModalButtons(true, buttons);
            });

        window[async](load);
    });

    $('#refresh-console').click(function (event) {
        event.preventDefault();
        $('.widget-console').attr('src', function (i, val) {
            return val;
        });
    });
}

function showModal(call) {
    $(".modal-content").load(call, function () {
        $(".modal").modal('show');
    });
}

function closeModal() {
    $(".modal").modal('hide');
}

function setModalButtons(enabled, buttons) {
    if (enabled) {
        buttons.each(function () {
            $(this).button('reset');
            $(this).removeProp("disabled");
            $(this).css("cursor", "pointer");
        });
    } else {
        buttons.each(function () {
            $(this).button('loading');
            $(this).prop("disabled", "disabled");
            $(this).css("cursor", "not-allowed!important");
        });
    }
}

function refreshContent(container, url, load) {
    container.empty();
    opts = {
        lines: 17,
        length: 56,
        width: 4,
        radius: 10,
        scale: .35,
        corners: 0,
        color: '#df691a',
        opacity: 0.25,
        rotate: 0,
        direction: 1,
        speed: 1,
        trail: 60,
        fps: 20,
        zIndex: 2e9,
        className: 'spinner',
        top: '-20px',
        left: '215px',
        shadow: false,
        hwaccel: true,
        position: 'relative'
    };
    container.append($('<h1 class="loading-text">LOADING</h1>')
        .append(new Spinner(opts).spin().el));
    container.load(url, function () {
        if (!(load === undefined)) {
            spinners = [];
            window[load]();
            container.find('.loadable').each(function () {
                $(this).css("opacity", "0.5")
                    .prepend($('<h1 class="loading-text">LOADING</h1>')
                        .append(new Spinner(opts).spin().el));
            });
            var checkLoading = window.setInterval(function () {
                if (!window.checkLoading()) {
                    container.find('.loadable').each(function () {
                        $(this).css("opacity", "1");
                    });
                    $(".loading-text").remove();
                    window.clearInterval(checkLoading);
                }
            }, 1000);
        }
        else {
            $(".loading-text").remove();
        }
    });
}

window.checkLoading = function () {
    if (window.loading) {
        return window.loading;
    } else {
        return false;
    }
};

function switchPageContent(container, link, url, load) {
    refreshContent(container, url, load);
    switchActiveNav(link);
}

function switchActiveNav(link) {
    $(".nav-sidebar").each(function () {
        pills = $(this).find('li');
        pills.each(function () {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
            }
        })
    });
    pill = $(link).parent();
    if (!pill.hasClass('active')) {
        pill.addClass('active');
    }
}

function formatString(string) {
    for (var i = 0; i < string.length; i++) {
        if (string[i] === ' ') {
            string = string.replace(' ', '!');
        }
    }
    return string;
}

function formatCall(call) {
    for (var i = 0; i < call.length; i++) {
        if (call[i] === '/') {
            call = call.replace('/', '!');
        }
    }
    return call;
}

// ---------------- //
// CONSOLE ACTIONS
// ---------------- //

var consoleLinks = new HashTable();

// ---------------- //
// CSRF
// ---------------- //

var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

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
// UI VALIDATION
// ---------------- //

var standardStringMin = 3;
var standardStringMax = 32;

function flagError(input, t) {
    $(input).parent().find(".error").remove();
    $(input).after('<p class="error text-danger">' + t + '</p>');
    $(input).parent().addClass("has-warning")
}

function clearUiValidation() {
    $('.error').each(function () {
        $(this).fadeOut().remove();
    });
}

function resetUiValidation(fields) {
    $(fields).val("").removeClass("ui-state-error");
    $('.error').each(function () {
        $(this).fadeOut().remove();
    });
}

function checkRequired(o, n) {
    if (o.val() == "" || o.val() == undefined || o.val() == "None") {
        flagError(o, n + " is required.");
        return false;
    } else {
        return true;
    }
}

function checkLength(o, n, min, max) {
    if (o.val().length > max || o.val().length < min) {
        flagError(o, n + " must be between " + min + " and " + max + ".");
        return false;
    } else {
        return true;
    }
}

function checkPassword(input) {
    if (input.val().length > 16 || input.val().length < 8) {
        flagError(input, "Password must be between 8 and 16 characters.");
        return false;
    } else {
        return true;
    }
}

function checkPasswordMatch(p, c) {
    if (p.val() != c.val()) {
        flagError(c, "Passwords do not match.");
        return false;
    } else {
        return true;
    }
}

function checkCharfield(o, n) {
    var regexp = /([0-9a-zA-Z_])+$/i;
    if (!( regexp.test(o.val()))) {
        o.addClass("ui-state-error");
        flagError(
            o, n + " may consist of letters, numbers and underscores.");
        return false;
    } else {
        return true
    }
}

function checkRange(o, n, min, max) {
    if (o.val() > max || o.val() < min) {
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
    if (!urlregex.test(url.val())) {
        url.addClass("ui-state-error");
        flagError(
            url,
            "Invalid remote URL.");
        return false;
    } else {
        return true
    }
}

function checkFile(file) {
    if (file.val() == '') {
        file.addClass("ui-state-error");
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
        name.addClass("ui-state-error");
        flagError(
            name,
            "Name is already in use.");
    }

    return pass;
}

function checkSize(o, n, min, max) {
    var unlimited = max == 0;
    if (unlimited) {
        if (o.val() < min || isNaN(Number(o.val()))) {
            o.addClass("ui-state-error");
            flagError(o, n);
            return false;
        } else {
            return true;
        }
    } else {
        if (o.val() < min || o.val() > max || isNaN(Number(o.val()))) {
            o.addClass("ui-state-error");
            flagError(o, n);
            return false;
        } else {
            return true;
        }
    }
}

function checkBootSize(o, f) {
    var flavorSize = flavors.items[f].disk_space + flavors.items[f].swap;
    if (o.val() < flavorSize) {
        o.addClass("ui-state-error");
        flagError(
            o,
            "Instance with flavor " + f + " boot volume must be " + flavorSize + "(gb) in size.");
        return false;
    } else {
        return true;
    }
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
    };
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
    users: 0, groups: 0, keys: 0
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
            $(id).fadeIn('fast').css("display", "inline-block");
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

var disabledActions = new HashTable();

function disableActions(id, bool) {

    var actions = '.' + id;
    var activeColor = '#AD682B';
    var disabledColor = '#696969';

    if (bool) {
        if (disabledActions.hasItem(actions)) {
            disabledActions.items[actions].count++;
        } else {
            disabledActions.setItem(actions, {count: 1});
            $(actions).bind('click', false);
            $(actions).css('color', disabledColor);
        }
    } else {
        disabledActions.items[actions].count--;
        if (disabledActions.items[actions].count <= 0) {
            $(actions).unbind('click', false);
            $(actions).css('color', activeColor);
            disabledActions.removeItem(actions);
        }
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

function setVisibleInLineBlock(selector, bool) {
    if (bool) {
        if ($(selector).css('display', 'none')) {
            $(selector).fadeIn('fast');
        }
    } else {
        if ($(selector).css('display', 'inline-block')) {
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
        $(select).append(
            '<option value="' + hashTable.items[item].value + '">' + hashTable.items[item].option + '</option>'
        );
    }
}

function removeFromSelect(value, select, hashTable) {
    hashTable.removeItem(value);
    refreshSelect(select, hashTable);
}

function addToSelect(value, option, select, hashTable) {
    hashTable.setItem(value, {value: value, option: option});
    refreshSelect(select, hashTable);
}

function hideSection(tableSelector, wellSelector, iconSelector) {

    // Let's assume the content is hidden for now
    var isHidden = true;

    $(wellSelector).each(function (input, element) {
        if (!$(element).hasClass("well-hidden")) {
            // if ANY of the children of the selected "well" element DOES NOT have a class of well-hidden, then the
            // section can't be hidden, so we set isHidden to false and break the loop
            isHidden = false;
            return false;
        }
    });

    if (isHidden) {

        $(tableSelector).show(0);
        $(wellSelector).removeClass("well-hidden");
        $(iconSelector).text("-");
        isHidden = false;
    } else {

        $(tableSelector).hide(0);
        $(wellSelector).addClass("well-hidden");
        $(iconSelector).text("+");
        isHidden = true;
    }
}

// --- INSTANCE MANAGEMENT

var instances = new HashTable(),
    instanceSnaps = new HashTable(),
    instanceOpts = new HashTable(),
    secGroupInstOpts = new HashTable(),
    secKeyInstOpts = new HashTable(),
    privNetInstOpts = new HashTable(),
    images = new HashTable(),
    flavors = new HashTable(),
    fips = new HashTable(),
    assignableFips = new HashTable(),
    assignableInstances = new HashTable();

function checkAssignFip() {

    if (assignableFips.length > 0 && assignableInstances.length > 0) {
        setVisible('#assign_ip', true);
    } else {
        setVisible('#assign_ip', false);
    }
}

function changeImageLocation(input, local, remote) {
    var localLabel = $('label[for="' + local.attr('id') + '"]'),
        remoteLabel = $('label[for="' + remote.attr('id') + '"]');

    if (input.val() == "image_url") {
        local.hide(0);
        localLabel.hide(0);
        remote.show(0);
        remoteLabel.show(0);
    }
    else {
        remote.hide(0);
        remoteLabel.hide(0);
        local.show(0);
        localLabel.show(0);
    }
    return true;
}

function startProgressBarUpdate(upload_id, form) {
    // This function will update the progress bar every second with the progress of the remote upload.
    // The progress is determined by querying the server for the current progress.

    var g_progress_intv = 0,
        bar = form.find('.upload-bar'),
        percent = form.find('.upload-percent');

    if (g_progress_intv != 0)
        clearInterval(g_progress_intv);

    g_progress_intv = setInterval(function () {
        $.getJSON("/get_upload_progress/" + upload_id, function (data) {
            if (data.status == "error") {

                // We got an error back so display the message and stop updating the progress bar.
                messages.showMessage("error", data.message);
                clearInterval(g_progress_intv);
                g_progress_intv = 0;
                return;
            }

            if (data.length == -1) {

                percentage = "100%";
                bar.width(percentage);
                percent.html(percentage);
                clearInterval(g_progress_intv);
                g_progress_intv = 0;
                return;
            }

            length = parseInt(data.length);
            if (length > 0)
                var percentage = Math.floor(100 * parseInt(data.uploaded) / length);
            else
                var percentage = 0;

            percentage = percentage + "%";
            bar.width(percentage);
            percent.html(percentage);
        });
    }, 1000);
}

function resetProgressBar(form) {
    var bar = form.find('.upload-bar'),
        percent = form.find('.upload-percent');

    var percentage = "0%";
    bar.width(percentage);
    percent.html(percentage);
}

// --- STORAGE

var volumes = new HashTable(),
    volumeTypes = new HashTable(),
    totalStorage = 0,
    usedStorage = 0,
    availableStorage = 0,
    attachableInstances = new HashTable(),
    snapshots = new HashTable(),
    snapshotVolumes = new HashTable();

function getStorage(projectId) {
    $.getJSON('/projects/' + projectId + '/get_project_quota/')
        .done(function (data) {
            totalStorage = data.gigabytes;
            updateUsedStorage();
            updateStorageBar()
        })
}

function updateUsedStorage() {

    usedStorage = 0;

    for (var volume in volumes.items) {
        var size = volumes.getItem(volume).size;
        usedStorage += Number(size);
    }

    availableStorage = totalStorage - usedStorage;
}

function updateStorageBar() {

    var bar = $(".volume-available-storage-bar"),
        label = $(".volume-available-storage-label");

    // Initialize storage bar
    var percent = (usedStorage / totalStorage) * 100;
    bar.progressbar({value: percent});
    label.empty();
    label.append(usedStorage + "/" + totalStorage);
}

function updateRevertVolumeSnapshots(volumeId) {

    var select = $("#revert_snapshot_name");
    select.empty();

    for (var snap in snapshots.items) {
        if (snapshots.items[snap].volumeId == volumeId) {
            select.append(
                '<option value="' + snap + '">' + snapshots.getItem(snap).name + '</option>'
            );
        }
    }
}

function changeSelectPreexistingVolume(select) {
    if ($(select).val() != "create") {
        $("#bam-volume-name").prop("disabled", "disabled");
        $("#bam-volume-size").prop("disabled", "disabled");
        $("#bam-volume-type").prop("disabled", "disabled");
    } else {
        $("#bam-volume-name").removeProp("disabled");
        $("#bam-volume-size").removeProp("disabled");
        $("#bam-volume-type").removeProp("disabled");
    }
}

// --- SOFTWARE DEFINED NETWORKS

var routers = new HashTable(),
    privNetRoutOpts = new HashTable(),
    privateNetworks = new HashTable();

function checkCreateRouter() {

    if (privNetRoutOpts.length > 0) {
        setVisible('#create-router', true);
    } else {
        setVisible('#create-router', false);
    }
}

// --- USERS/SECURITY

var users = new HashTable(),
    usernames = new HashTable(),
    orphanedUserOpts = new HashTable(),
    securityGroups = new HashTable(),
    secGroupPorts = [],
    tcpPorts = [],
    udpPorts = [],
    tcpString = "",
    udpString = "",
    icmp = "";

function checkAddUser() {
    if (orphanedUserOpts.length > 0) {
        setVisible("#add-existing-user", true);
    } else if (orphanedUserOpts.length <= 0) {
        setVisible("#add-existing-user", false);
    }
}

function getSecGroupPorts() {
    var tcpCount = 0;
    var udpCount = 0;

    tcpPorts = [];
    udpPorts = [];
    icmp = "disabled";

    for (var portCount = 0; portCount < secGroupPorts.length; portCount++) {

        if (secGroupPorts[portCount].transport == "tcp") {
            tcpPorts[tcpCount] = parseInt(secGroupPorts[portCount].from_port);
            tcpCount++;
        }

        if (secGroupPorts[portCount].transport == "udp") {
            udpPorts[udpCount] = parseInt(secGroupPorts[portCount].from_port);
            udpCount++;
        }

        if (secGroupPorts[portCount].transport == "icmp") {
            icmp = "enabled";
        }
    }

    tcpPorts.sort(function (a, b) {
        return a - b;
    });

    udpPorts.sort(function (a, b) {
        return a - b;
    });
}

function updateSecGroupPorts(newPorts) {
    secGroupPorts = [];
    for (var i = 0; i < newPorts.length; i++) {
        secGroupPorts[i] = {
            from_port: newPorts[i].from_port,
            to_port: newPorts[i].to_port,
            transport: newPorts[i].transport
        };
    }

    getSecGroupPorts();
}

function updateTcpString() {
    tcpString = "";
    for (var i = 0; i < tcpPorts.length; i++) {
        if (tcpPorts[i] > 0) {
            tcpString += tcpPorts[i];
            if (i + 1 < tcpPorts.length) {
                tcpString += ",";
            }
        }
    }
}

function updateUdpString() {
    udpString = "";
    for (var j = 0; j < udpPorts.length; j++) {
        if (udpPorts[j] > 0) {
            udpString += udpPorts[j];
            if (j + 1 < udpPorts.length) {
                udpString += ",";
            }
        }
    }
}

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

