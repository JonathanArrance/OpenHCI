$(function () {
    // Declare Page Container
    var page = $("#page-content"),
        project = $("#project-container"),
        instances = $("#instances-container"),
        storage = $("#storage-container"),
        networking = $("#networking-container"),
        usersSecurity = $("#users-security-container");

    // --- Sidebar Nav ---
    $("#project").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
        window.loading.current = project;
    });

    $("#instances").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, instances, [], "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
        window.loading.current = instances;
    });

    $("#storage").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, storage, [], "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
        window.loading.current = storage;
    });

    $("#networking").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, networking, [], "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
        window.loading.current = networking;
    });

    $("#users-security").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, usersSecurity, [], "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
        window.loading.current = usersSecurity;
    });

    // --- Click Events ---

    // Project
    $(document).on('click', '#delete-project', function (event) {
        event.preventDefault();
        var title = formatSpaces($(this).data("title")),
            message = formatSpaces($(this).data("message")),
            call = formatCall($(this).data("call")),
            notice = formatSpaces($(this).data("notice")),
            refresh = formatCall("redirect-to:/cloud/manage/"),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Instances
    $(document).on('click', '.instance-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    // Storage
    $(document).on('click', '.volume-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });
    $(document).on('click', '.create-snapshot', function(event){
        event.preventDefault();
        showConfirmModal('/snapshot/get/create/' + $(this).data("volume") + '/');
    });

    // Networking
    $(document).on('click', "#allocate-ip", function (event) {
        event.preventDefault();
        showMessage('info', "Allocating IP.");

        $.getJSON('/allocate_floating_ip/' + CURRENT_PROJECT_ID + '/' + DEFAULT_PUBLIC + '/')
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                }
                if (data.status == 'success') {
                    showMessage('success', "Successfully allocated " + data.ip_info.floating_ip + ".");
                    refreshContainer(page, networking, "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
                }
            })
            .fail(function () {
                showMessage('error', 'Server Fault');
            })
    });

    // --- Initialize Project View ---
    window.loading.current = page;
    switchPageContent($("#project"), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
    $("#project").addClass('active');
});

// --- Project Charts ---

charts = {};

function generateQuotaBar(parent, project_used, project_total, label, limit_used, classes) {
    if (parent.find('div.quota-bar').length == 0) {
        limit_used = limit_used === undefined ? limit_used = false : parseInt(limit_used);
        classes = classes === undefined ? ["progress-bar-info", "progress-bar-success", "progress-bar-warning"] : classes;
        project_used = parseInt(project_used);
        project_total = parseInt(project_total);
        var html = $('<div class="progress"></div>');
        if (limit_used != false) {
            var usedWidth = ((project_used / project_total) * 100),
                totalWidth = ((limit_used / project_total) * 100);
            totalWidth = totalWidth - usedWidth;
            if (usedWidth <= totalWidth) {
                html
                    .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + "%" + '"></div>'))
                    .append($('<div class="progress-bar ' + classes[1] + '" style="width: ' + totalWidth + "%" + '"></div>'));
            } else {
                html
                    .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + "%" + '"></div>'));
            }
            html = $('<div class="quota-bar"><h5>' + label + ' ' + project_used + '/' + limit_used + '/' + project_total + '</h5></div>').append(html);
        } else {
            var usedWidth = ((project_used / project_total) * 100);
            html
                .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + "%" + '"></div>'));
            html = $('<div class="quota-bar"><h5>' + label + ' ' + project_used + '/' + project_total + '</h5></div>').append(html);
        }
        parent.append(html);
    }
}

function generateQuotaPie(id, data, label) {
    if (data.length == 2) {
        var used = data[0],
            max = data[1];
        data = [
            [used[0], used[1]],
            [max[0], (max[1] - used[1])]
        ];
    } else if (data.length == 3) {
        var used = data[0],
            util = data[1],
            max = data[2];
        if (used[0] >= util[0]) {
            data = [
                [used[0], used[1]],
                [max[0], (max[1] - used[1])]
            ];
        } else {
            data = [
                [used[0], used[1]],
                [util[0], (util[1] - used[1])],
                [max[0], (max[1] - (used[0] + util[0]))]
            ];
        }
    }
    charts[id] = generatePie(id, data, label);

}
function generateInstanceBars(meters, stats) {
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