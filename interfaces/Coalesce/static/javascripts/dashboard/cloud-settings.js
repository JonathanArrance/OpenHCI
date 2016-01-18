$(function () {
    // Click Events
    // Toggle MFA
    $(document).on('click', '.enable-mfa', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = "/third_party_authentication/get/".slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Toggle default projects
    $(document).on('click', '.disable-mfa', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = "/third_party_authentication/get/".slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });
});