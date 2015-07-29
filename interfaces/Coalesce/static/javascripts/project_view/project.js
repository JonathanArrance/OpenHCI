$(function () {
    // Declare Page Container
    var page = $("#page-content"),
        project = $("#project-container"),
        instances = $("#instances-container"),
        storage = $("#storage-container"),
        networking = $("#networking-container");

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

    // --- Click Events ---

    // Initialize Project View
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
            if (usedWidth <= totalWidth){
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

function generateQuotaPie(id, data, label){
    data = [[data[0][0], data[0][1]], [data[1][0], (data[1][1] - data[0][1])]];
    charts[id] = generatePie(id, data, label);
}