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

    // View elements
    var status = $('#instance-status'),
        consoleWindow = $('#instance-console'),
        actions = $('#widget-actions'),
        progressbar = $('#instance-progressbar');

    $("#instance-view-reboot-confirm-form").dialog({
        autoOpen: false,
        height: 125,
        width: 235,
        modal: true,
        buttons: {
            "Confirm": function () {

                messages.showMessage('notice', 'Rebooting');

                // Hide other actions
                actions.slideUp();

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                emptyAndAppend(status, "REBOOT");

                $.getJSON('/server/' + PROJECT_ID + '/' + SERVER_ID + '/reboot/')
                    .done(function (data) {

                        if (data.status == "error") {

                            messages.showMessage('error', data.message);
                        }

                        if (data.status == "success") {

                            messages.showMessage('success', data.message);
                            emptyAndAppend(status, "ACTIVE");
                        }
                    })
                    .fail(function () {

                        messages.showMessage('error', 'Server Fault');
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
                        setVisible(progressbar, false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $('#reboot-server').click(function () {
        $("#instance-view-reboot-confirm-form").dialog("open");
    });
});


