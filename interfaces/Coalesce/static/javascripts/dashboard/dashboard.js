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
        var title = formatSpaces($(this).data("title")),
            message = formatSpaces($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = formatSpaces($(this).data("notice")),
            async = $(this).data("async");
        showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
    });

    // Upgrade
    $(document).on('click', '.upgrade', function (event) {
        event.preventDefault();
        var title = formatSpaces($(this).data("title")),
            message = formatSpaces($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = formatSpaces($(this).data("notice")),
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

// --- Dashboard Charts ---

charts = {};

function getCeilometerStats() {
    var endDate = new Date(),
        startDate = new Date(endDate),
        durationInMinutes = 4320;
    startDate.setUTCMinutes(endDate.getUTCMinutes() - durationInMinutes);
    var startTimeString = startDate.getUTCFullYear() + "-" + (startDate.getUTCMonth() + 1 ) + "-" + startDate.getUTCDate() + "T" + ("0" + startDate.getUTCHours()).slice(-2) + "%3A" + ("0" + startDate.getUTCMinutes()).slice(-2),
        endTimeString = endDate.getUTCFullYear() + "-" + (endDate.getUTCMonth() + 1) + "-" + endDate.getUTCDate() + "T" + ("0" + endDate.getUTCHours()).slice(-2) + "%3A" + ("0" + endDate.getUTCMinutes()).slice(-2);

    $.getJSON('ceilometer/get/meters/dashboard/').done(function (data) {
        if (data.message) {
            showMessage("error", "Error getting gauges")
        } else {
            var callString = "";
            $(data).each(function (index, element) {
                var meterString = callString == "" ? "" : ",";
                $(element.meters).each(function (key, value) {
                    meterString += value.meterType;
                    if (key + 1 != element.meters.length) {
                        meterString += ","
                    }
                });
                callString += meterString;
            });

            var call = USER_LEVEL > 0
                ? 'ceilometer/get/statistics/' + startTimeString + '/' + endTimeString + '/' + callString + '/' + USER_ID + '/'
                : 'ceilometer/get/statistics/' + startTimeString + '/' + endTimeString + '/' + callString + '/';
            $.getJSON(call)
                .done(function (stats) {
                    if (stats.status == "success") {
                        if (stats.message != "empty dataset") {
                            for (var stat in stats.statistics) {
                                var chartType = stats.statistics[stat].meter_type;
                                if (chartType == "cpu_util") {
                                    chartType = "cpu-util";
                                } else {
                                    for (var i = 0; i < chartType.length; i++) {
                                        if (chartType[i] == ".") {
                                            chartType = chartType.replace(".", "-");
                                        }
                                    }
                                }
                                charts[chartType].load({
                                    columns: [
                                        ['data', stats.statistics[stat].avg.toFixed(0)]
                                    ]
                                });
                            }
                        } else {
                            showMessage('error', "Error getting Ceilometer statistics");
                        }
                    }
                })
        }
    });
}

function startGaugeUpdateTimer() {
    if (window.gaugeTimer) {
        window.clearInterval(window.gaugeTimer);
    }
    window.gaugeTimer = setInterval(function () {
        getCeilometerStats();
    }, 30000)
}