$(function () {

    // CSRF protection
    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Form elements
    var flavor = $("#flavor");

    // View elements
    var status = $('#instance-status'),
        consoleWindow = $('#instance-console'),
        actions = $('#widget-actions'),
        progressbar = $('#instance-progressbar');

    $("#instance-view-resize-dialog-form").dialog({
        autoOpen: false,
        height: 175,
        width: 235,
        modal: true,
        buttons: {
            "Resize Instance": function () {

                var confirmedFlavor = $(flavor).find("option:selected").val();

                message.showMessage('notice', "Resizing " + $('#instance-name').text() + " to " + flavor.text() + ".");

                actions.slideUp();

                // Initialize progressbar and make it visible if hidden
                progressbar.progressbar({value: false});
                disableProgressbar(progressbar, "instances", false);

                emptyAndAppend(status, "RESIZE");

                $.getJSON('/server/' + PROJECT_ID + '/' + SERVER_ID + '/' + confirmedFlavor + '/resize_server/')
                    .done(function (data) {

                        if (data.status == "error") {

                            message.showMessage('error', data.message);
                            emptyAndAppend(status, "ACTIVE");
                        }

                        if (data.status == "success") {

                            message.showMessage('success', data.message);
                            emptyAndAppend(status, "ACTIVE");
                            emptyAndAppend('#instance-flavor', confirmedFlavor);
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', "Server Fault");
                        emptyAndAppend(status, "ERROR");
                    })
                    .always(function () {

                        $('#instance-console-refresh-confirm-form').dialog({
                            resizable: false,
                            autoOpen: true,
                            height: 125,
                            width: 235,
                            modal: true,
                            buttons: {
                                "Yes": function () {

                                    $(consoleWindow).attr('src', function (i, val) {
                                        return val;
                                    });
                                    $(this).dialog("close");
                                },
                                "No": function () {

                                    $(this).dialog("close");
                                }
                            },
                            close: function () {
                            }
                        });

                        actions.slideDown();
                        disableProgressbar(progressbar, "instances", true);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#resize-server")
        .click(function () {
            $("#instance-view-resize-dialog-form").dialog("open");
        });
});
