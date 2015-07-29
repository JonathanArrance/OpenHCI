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
    $(document).on('click', '.instance-name a', function (event) {
        event.preventDefault();
        var title,
            call = $(this).data("call"),
            container = "#instance-container",
            refresh = $(this).data("refresh");
        $($('<div id="instance-modal" class="modal">').load(call, function () {
            $(this).modal('show');
        }));
        //, {'container': container, 'refresh': refresh}
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