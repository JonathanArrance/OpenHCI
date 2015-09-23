$(function(){
    var page = $("#main-page-content");
    $("#logging-in-to-instances").click(function (event) {
        event.preventDefault();
        showInfoModal(page, "/guides/get/logging_in_to_instances/");
    });
    $("#creating-instances").click(function (event) {
        event.preventDefault();
        showInfoModal(page, "/guides/get/creating_instances/");
    });
});