$(function () {
    // Declare Page Container
    var page = $("#page-content"),
        project = $("#project-container");

    // --- Sidebar Nav ---
    $("#project-panel").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
        window.loading.current = project;
    });

    // --- Click Events ---

    // Initialize Project View
    window.loading.current = page;
    switchPageContent($("#project-panel"), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
    $("#project-panel").addClass('active');
});

function generateQuotaBar(parent, project_used, project_total, label, classes, limit_used, limit_max) {
    if (parent.find('div.quota-bar').length == 0) {
        classes = classes === undefined ? ["progress-bar-info", "progress-bar-success", "progress-bar-warning"] : classes;
        limit_used = limit_used === undefined ? limit_used = false : parseInt(limit_used);
        limit_max = limit_max === undefined ? limit_max = false : parseInt(limit_max);
        project_used = parseInt(project_used);
        project_total = parseInt(project_total);
        var html = $('<div class="progress"></div>');
        if (limit_used != false && limit_max != false) {
            var usedWidth = ((project_used / limit_max) * 100) + "%",
                totalWidth = ((project_total / limit_max) * 100) + "%",
                limitWidth = ((limit_used / limit_max) * 100) + "%";
            html
                .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + '"></div>'))
                .append($('<div class="progress-bar ' + classes[1] + '" style="width: ' + totalWidth + '"></div>'))
                .append($('<div class="progress-bar ' + classes[2] + '" style="width: ' + limitWidth + '"></div>'))
                .append($('<span>' + project_used + '/' + project_total + '/' + limit_used + '/' + limit_max + '</span>'));
        } else {
            var usedWidth = ((project_used / project_total) * 100) + "%";
            html
                .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + '"></div>'))
                .append($('<span>' + project_used + '/' + project_total + '</span>'));
        }

        html = $('<div class="quota-bar"><h5>' + label + '</h5></div>').append(html);

        parent.append(html);
    }
}