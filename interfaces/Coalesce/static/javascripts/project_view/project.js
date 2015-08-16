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
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("redirect-to:/cloud/manage/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    $(document).on('click', '#update-quotas', function (event) {
        event.preventDefault();
        showLoader(page);
        showConfirmModal('/projects/get/update_quotas/' + CURRENT_PROJECT_ID + '/');
    });

    // Instances
    $(document).on('click', '.instance-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', '#create-instance', function (event) {
        event.preventDefault();
        showLoader(page);
        showConfirmModal('/instance/get/create/' + CURRENT_PROJECT_ID + '/');
    });

    $(document).on('click', '.delete-instance, .pause-instance, .unpause-instance, .suspend-instance, .resume-instance, .power-on-instance, .power-off-instance, .power-cycle-instance, .reboot-instance', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Images
    $(document).on('click', '.import-image', function (event) {
        event.preventDefault();
        showLoader(page);
        showConfirmModal('/image/get/import/');
    });

    $(document).on('click', '.delete-image', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Flavors
    $(document).on('click', '.create-flavor', function (event) {
        event.preventDefault();
        showLoader(page);
        showConfirmModal('/flavor/get/create/');
    });

    $(document).on('click', '.delete-flavor', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Storage
    $(document).on('click', '.volume-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', '.create-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/create/' + CURRENT_PROJECT_ID + '/');
    });

    $(document).on('click', '.attach-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/attach/' + CURRENT_PROJECT_ID + '/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.revert-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/revert/' + CURRENT_PROJECT_ID + '/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.clone-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/clone/' + CURRENT_PROJECT_ID + '/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.create-snapshot', function (event) {
        event.preventDefault();
        showConfirmModal('/snapshot/get/create/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.create-volume-from-snapshot', function (event) {
        event.preventDefault();
        showConfirmModal('/snapshot/get/create_volume/' + CURRENT_PROJECT_ID + '/' + $(this).data("snapshot") + '/');
    });

    $(document).on('click', '.detach-volume, .delete-volume, .delete-snapshot', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Networking
    $(document).on('click', '.network-name button, .router-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

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

    $(document).on('click', '.assign-ip', function (event) {
        event.preventDefault();
        showConfirmModal('/floating_ip/get/assign/' + CURRENT_PROJECT_ID + '/' + $(this).data("ip") + '/');
    });

    $(document).on('click', ".deallocate-ip, .delete-network, .delete-router", function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    $(document).on('click', '.create-network', function (event) {
        event.preventDefault();
        showConfirmModal('/network/get/create/');
    });

    $(document).on('click', '.create-router', function (event) {
        event.preventDefault();
        showConfirmModal('/router/get/create/' + CURRENT_PROJECT_ID + "/");
    });

    // Users/Security
    $(document).on('click', '.user-name button, .group-name button, .key-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', '.create-user', function (event) {
        event.preventDefault();
        showConfirmModal('/user/get/create/');
    });

    $(document).on('click', '.add-user', function (event) {
        event.preventDefault();
        showConfirmModal('/user/get/add/');
    });

    $(document).on('click', '.create-group', function (event) {
        event.preventDefault();
        showConfirmModal('/security_group/get/create/');
    });

    $(document).on('click', '.create-key', function (event) {
        event.preventDefault();
        showConfirmModal('/key_pair/get/create/');
    });

    $(document).on('click', '.delete-user, .enable-user, .disable-user, .remove-user, .delete-group, .delete-key', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    $("#instance-wizard").click(function (event) {
        event.preventDefault();
        showConfirmModal('/projects/get/instance_wizard/' + CURRENT_PROJECT_ID + '/');
    });

    // --- Initialize Project View ---
    window.loading.current = page;
    window.startProjectUpdateTimer();
    switchPageContent($("#project"), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
    window.loading.current = project;
    $("#project").addClass('active');
});

window.deleteTimer = function () {
    window.setInterval(function () {
    }, 1000)
};

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

window.updateProjectContent = function () {
    var page = $("#page-content"),
        project = $("#project-container"),
        instances = $("#instances-container"),
        storage = $("#storage-container"),
        networking = $("#networking-container"),
        usersSecurity = $("#users-security-container");
    switch (window.loading.current.selector) {
        case project.selector:
            stealthRefreshContainer(page, project, "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
            break;
        case instances.selector:
            stealthRefreshContainer(page, instances, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
            break;
        case storage.selector:
            stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
            break;
        case networking.selector:
            stealthRefreshContainer(page, networking, "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
            break;
        case usersSecurity.selector:
            stealthRefreshContainer(page, usersSecurity, "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
            break;
    }
};

window.startProjectUpdateTimer = function () {
    if (window.projectUpdateTimer) {
        window.clearInterval(window.projectUpdateTimer);
    }
    window.projectUpdateTimer = setInterval(function () {
        window.updateProjectContent();
    }, 60000)
};