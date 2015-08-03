$(function () {
    // Declare Page Container
    var page = $("#page-content"),
        node = $("#node-container"),
        project = $("#project-container"),
        tps = $("#tps-container"),
        metering = $("#metering-container"),
        account = $("#account-container");

    // --- Sidebar Nav ---
    $("#node-stats").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, node, [], "/nodes/get_stats/");
        window.loading.current = node;
    });

    $("#project-stats").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, project, [], "/projects/get_stats/");
        window.loading.current = project;
    });

    $("#third-party-storage").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, tps, [], "/third_party_storage/get/");
        window.loading.current = tps;
        window.startDonutUpdateTimer();
    });

    $("#metering").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, metering, ["getCeilometerStatistics"], "/metering/get/");
        window.loading.current = metering;
        startGaugeUpdateTimer();
    });

    $("#account").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, account, [], "/user/" + PROJECT_NAME + "/" + PROJECT_ID + "/" + USERNAME + "/account_view/");
        window.loading.current = account
    });

    // --- Click Events ---
    // Update Password
    $(document).on('click', '.update-password', function (event) {
        event.preventDefault();
        var call = '/get_update_account_password/';
        showConfirmModal(call);
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
            button = $(this),
            isValid = checkPassword(inputs.new) && checkPasswordMatch(inputs.new, inputs.confirm);
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
        var title = encodeString($(this).data("title")),
            message = encodeString($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = encodeString($(this).data("notice")),
            refresh = formatCall("/user/" + PROJECT_NAME + "/" + PROJECT_ID + "/" + USERNAME + "/account_view/"),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/'+ refresh + '/' + async + '/');
    });

    // Upgrade
    $(document).on('click', '.upgrade', function (event) {
        event.preventDefault();
        var title = encodeString($(this).data("title")),
            message = encodeString($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = encodeString($(this).data("notice")),
            refresh = formatCall("/user/" + PROJECT_NAME + "/" + PROJECT_ID + "/" + USERNAME + "/account_view/"),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Initialize Dashboard
    if (USER_LEVEL == 0) {
        // On page load, get node stats and make that page content, set Node Stats link as active
        window.loading.current = page;
        switchPageContent($("#node-stats"), page, window.loading.current, node, [], "/nodes/get_stats/");
        $("#node-stats").addClass('active');
    } else {
        // On page load, get account view and make that page content, set account view link as active
        window.loading.current = page;
        switchPageContent($("#account"), page, window.loading.current, node, [], "/user/" + PROJECT_NAME + "/" + PROJECT_ID + "/" + USERNAME + "/account_view/");
        $("#account").addClass('active');
    }
});

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

function generateDashBars(meters, stats) {
    meters = JSON.parse(meters.jsonify());
    stats = JSON.parse(stats.jsonify());
    var counters = [],
        groups = [];
    $(stats).each(function (index, stat) {
        if (stat.chartType == "counter") {
            counters.push(stat);
        }
    });
    var barGroups = {};
    $(counters).each(function (index, element) {
        if (barGroups[element['meterName'].split(".")[0]] === undefined) {
            barGroups[element['meterName'].split(".")[0]] = [];
        }
        barGroups[element['meterName'].split(".")[0]].push(element);
    });
    for (var bar in barGroups) {
        var data = [],
            units,
            id;
        $(barGroups[bar]).each(function (a, statsMeter) {
            $(meters).each(function (b, meterGroup) {
                $(meterGroup.meters).each(function (c, meter) {
                    if (meter.meterType == statsMeter.meterName) {
                        data.push([meter.label, statsMeter.utilization]);
                        units = statsMeter.unitMeasurement;
                        id = meterGroup.id;
                    }
                });
            });
        });
        units = units === undefined ? "" :
            units == "B/s" ? "bytes/second" : units;
        id = id === undefined ? console.log("Bar group id never defined.") : id;
        groups.push([bar, units, data, id]);
    }
    $(groups).each(function (c, d) {
        if (document.getElementById(d[0]) === null) {
            var groupId = "#" + d[3];
            $(groupId).append($($('<div id="' + d[0] + '" class="col-sm-6 no-padding" style="margin-left:-15px;"></div>')));
            charts[d[0]] = generateBar(d[0], d[1], d[2]);
        }
    });
}

window.getCeilometerStats = function () {
    window.loading.add("getCeilometerStats");
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
            var callString = "",
                meters = [];
            $(data).each(function (a, meterGroup) {
                meters.push(meterGroup);
                var meterString = callString == "" ? "" : ",";
                $(meterGroup.meters).each(function (b, meter) {
                    meterString += meter.meterType;
                    if (b + 1 != meterGroup.meters.length) {
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
                        var counters = [],
                            groups = [];
                        $(stats.statistics).each(function (a, stat) {
                            if (stat.chartType == "radial") {
                                charts[stat.htmlID].load({
                                    columns: [
                                        ['data', stat.utilization.toFixed(0)]
                                    ]
                                });
                            } else if (stat.chartType == "counter") {
                                counters.push(stat);
                            }
                        });
                        var barGroups = {};
                        $(counters).each(function (index, counterStat) {
                            if (barGroups[counterStat['meterName'].split(".")[0]] === undefined) {
                                barGroups[counterStat['meterName'].split(".")[0]] = [];
                            }
                            barGroups[counterStat['meterName'].split(".")[0]].push(counterStat);
                        });
                        for (var bar in barGroups) {
                            var data = [];
                            $(barGroups[bar]).each(function (a, statsMeter) {
                                $(meters).each(function (b, meterGroup) {
                                    $(meterGroup.meters).each(function (c, meter) {
                                        if (meter.meterType == statsMeter.meterName) {
                                            data.push([meter.label, statsMeter.utilization]);
                                        }
                                    });
                                });
                            });
                            groups.push([bar, data]);
                        }
                        $(groups).each(function (a, group) {
                            charts[group[0]].load({columns: group[1]});
                        });
                    } else {
                        showMessage('error', "Error getting Ceilometer statistics");
                    }
                })
        }
    });
    window.loading.remove("getCeilometerStats");
};

window.startGaugeUpdateTimer = function () {
    if (window.gaugeTimer) {
        window.clearInterval(window.gaugeTimer);
    }
    window.gaugeTimer = setInterval(function () {
        getCeilometerStats();
    }, 60000)
};