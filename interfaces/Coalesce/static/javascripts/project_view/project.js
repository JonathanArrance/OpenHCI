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
