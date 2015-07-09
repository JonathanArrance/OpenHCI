$(function () {
    // Declare Page Container
    var page = $("#page-content");

    // --- Sidebar Nav ---
    $("#node-stats").click(function (event) {
        event.preventDefault();
        switchPageContent(page, $(this), "/nodes/get_stats/");
    });

    $("#project-stats").click(function (event) {
        event.preventDefault();
        switchPageContent(page, $(this), "/projects/get_stats/");
    });

    $("#third-party-storage").click(function (event) {
        event.preventDefault();
        switchPageContent(page, $(this), "/third_party_storage/get/");
    });

    $("#metering").click(function (event) {
        event.preventDefault();
        switchPageContent(page, $(this), "/metering/get/");
    });

    $("#account").click(function (event) {
        event.preventDefault();
        var user = $(this).data("user"),
            projectName = $(this).data("project-name"),
            projectId = $(this).data("project-id");
        switchPageContent(page, $(this), "/user/" + projectName + "/" + projectId + "/" + user + "/account_view/");
    });

    // --- Click Events ---
    // Update Password
    $(document).on('click', '.update-password', function (event) {
        event.preventDefault();
        var call = '/get_update_account_password/';
        showModal(call);
    });

    $(document).on('click', '#update-account-password', function (event) {
        event.preventDefault();
        clearUiValidation();
        var user = $(this).data("user"),
            level = $(this).data("user-level"),
            project = $(this).data("project"),
            inputs = {
                'current': $("#current-password"),
                'new': $("#new-password"),
                'confirm': $("#confirm-password")
            },
            button = $(this);
        var isValid =
            checkPassword(inputs.new) && checkPasswordMatch(inputs.new, inputs.confirm);
        if (isValid) {
            button.button('loading');
            button.prop("disabled", "disabled");
            showMessage('info', "Updating password ...");
            var call =
                level == 0
                    ? '/update_admin_password/' + inputs.current.val() + '/' + inputs.new.val() + '/'
                    : '/update_user_password/' + user + '/' + inputs.current.val() + '/' + inputs.new.val() + '/' + project + '/';
            $.getJSON(call)
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
                    button.button('reset');
                    button.removeProp("disabled");
                });
        }
    });

    // Phone Home
    $(document).on('click', '.phonehome', function (event) {
        event.preventDefault();
        var title = formatString($(this).data("title")),
            message = formatString($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = formatString($(this).data("notice")),
            async = $(this).data("async");
        showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
    });

    // Upgrade
    $(document).on('click', '.upgrade', function (event) {
        event.preventDefault();
        var title = formatString($(this).data("title")),
            message = formatString($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = formatString($(this).data("notice")),
            async = $(this).data("async");
        showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
    });

});

function initializeAdminDashboard() {
    container = $("#page-content");
    if (USER_LEVEL == 0) {
        // On page load, get node stats and make that page content, set Node Stats link as active
        link = $("#node-stats");
        pill = link.parent();
        url = "/nodes/get_stats/";
    } else {
        // On page load, get account view and make that page content, set account view link as active
        link = $("#account");
        pill = link.parent();
        url = "/user/" + PROJECT_NAME + "/" + PROJECT_ID + "/" + USERNAME + "/account_view/";
    }

    switchPageContent(container, link, url);
    pill.addClass('active');
}

window.getPhoneHomeMessage = (function (load) {
    $("#confirm-status").html("Initializing Phone Home ...");
    gettingPhonehomeMsg = false;
    phoneHomeMsg = window.setInterval(function () {
        if (!gettingPhonehomeMsg) {
            gettingPhonehomeMsg = true;
            var getMsg = $.getJSON('/phonehome/getmsg/')
                .done(function (data) {
                    $("#confirm-status").html(data.message);
                });
            $.when(getMsg).always(function () {
                gettingPhonehomeMsg = false;
            });
        }
    }, 5000);
    $.when(load).done(function () {
        clearInterval(phoneHomeMsg);
    });
});

window.getUpgradeMessage = (function (load) {
    $("#confirm-status").html("Initializing Upgrade ...");
    gettingUpgradeMsg = false;
    upgradeMessage = window.setInterval(function () {
        if (!gettingUpgradeMsg) {
            gettingUpgradeMsg = true;
            var getMsg = $.getJSON('/upgrade/getmsg/')
                .done(function (data) {
                    $("#confirm-status").html(data.message);
                });
            $.when(getMsg).always(function () {
                gettingUpgradeMsg = false;
            });
        }
    }, 5000);
    $.when(load).done(function () {
        clearInterval(upgradeMessage);
    });
});

// --- Dashboard Gauges ---

var gauges = [],
    calls = [],
    calls_complete = true;

function createGauge(name, label, meterType, calcType, min, max, minorTicks) {
    var config =
    {
        size: 120,
        label: label,
        meterType: meterType,
        calcType: calcType,
        min: undefined != min ? min : 0,
        max: undefined != max ? max : 1000,
        minorTicks: minorTicks
    };

    var range = config.max - config.min;
    config.yellowZones = [{from: config.min + range * 0.75, to: config.min + range * 0.9}];
    config.redZones = [{from: config.min + range * 0.9, to: config.max}];

    gauges[name] = new Gauge(name + "GaugeContainer", config);
    gauges[name].render();
}

function createGauges() {

    // 6 Fusion Meters
    createGauge("cpu", "CPU %", "cpu_util", "avg", 0, 100, 5);
    createGauge("memory", "Memory MB", "memory.usage", "avg", 0, 128000, 8);
    createGauge("storage", "Storage GB", "disk.root.size", "avg", 0, 1000, 8);
    createGauge("diskreadrate", "Disk Reads B/s", "disk.read.bytes.rate", "avg", 0, 100000, 8);
    createGauge("diskwriterate", "Disk Writes B/s", "disk.write.bytes.rate", "avg", 0, 100000, 8);
    createGauge("lanincomingrate", "LAN Incoming B/s", "network.incoming.bytes.rate", "avg", 0, 100000, 8);
    createGauge("lanoutgoingrate", "LAN Outgoing B/s", "network.outgoing.bytes.rate", "avg", 0, 100000, 8);
    createGauge("wanincomingrate", "WAN Incoming B/s", "wan.incoming.bytes.rate", "avg", 0, 100000, 8);
    createGauge("wanoutgoingrate", "WAN Outgoing B/s", "wan.outgoing.bytes.rate", "avg", 0, 100000, 8);

    // Core and Compute Meters
    createGauge("cpupercent", "% CPU", "compute.node.cpu.percent", "avg", 0, 100, 5);
    createGauge("cpuuserpercent", "% CPU User", "compute.node.cpu.user.percent", "avg", 0, 100, 5);
    createGauge("cpuidlepercent", "% CPU Idle", "compute.node.cpu.idle.percent", "avg", 0, 100, 5);
    createGauge("cpuiowaitpercent", "% CPU I/O Wait", "compute.node.cpu.iowait.percent", "avg", 0, 100, 5);
    createGauge("cpukernelpercent", "% CPU Kernel", "compute.node.cpu.kernel.percent", "avg", 0, 100, 5);
}

function updateGauges() {
    if (calls_complete) {
        calls_complete = false;
        calls = [];
        for (var key in gauges) {
            calls[calls.length] = getCeilometerResults(gauges[key], gauges[key].config.meterType, gauges[key].config.calcType)
        }

        $.when.apply(null, calls).done(function () {
            calls_complete = true;
        });
    }
}

function getCeilometerResults(guage, meterType, calcType) {
    var endDate = new Date();
    var startDate = new Date(endDate);
    var durationInMinutes = 4320;
    startDate.setUTCMinutes(endDate.getUTCMinutes() - durationInMinutes);
    var startTimeString = startDate.getUTCFullYear() + "-" + (startDate.getUTCMonth() + 1 ) + "-" + startDate.getUTCDate() + "T" + ("0" + startDate.getUTCHours()).slice(-2) + "%3A" + ("0" + startDate.getUTCMinutes()).slice(-2);
    var endTimeString = endDate.getUTCFullYear() + "-" + (endDate.getUTCMonth() + 1) + "-" + endDate.getUTCDate() + "T" + ("0" + endDate.getUTCHours()).slice(-2) + "%3A" + ("0" + endDate.getUTCMinutes()).slice(-2);
    var url = "ceilometer/get/statistics/" + startTimeString + "/" + endTimeString + "/" + meterType + "/";

    call_complete = $.getJSON(url).done(function (data) {
        if (data.status == "success") {
            if (data.message != "empty dataset") {
                var result = data.statistics[0][calcType];
                guage.redraw(result);
            }
        }
    });

    return call_complete;
}

function initializeGauges() {
    createGauges();
    updateGauges();
    window.setInterval(updateGauges, 60000);
}