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

    $("#instance-view-poweron-confirm-form").dialog({
        autoOpen: false,
        height: 125,
        width: 235,
        modal: true,
        buttons: {
            "Confirm": function () {

                message.showMessage('notice', 'Powering On');

                // Hide other actions
                actions.slideUp();

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                $.getJSON('/server/' + PROJECT_ID + '/' + SERVER_ID + '/power_on_server/')
                    .done(function (data) {

                        if (data.status == "error") {

                            message.showMessage('error', data.message);
                        }

                        if (data.status == "success") {

                            message.showMessage('success', data.message);
                            emptyAndAppend(status, "ACTIVE");
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');
                        emptyAndAppend(status, "ERROR");
                    })
                    .always(function (data) {

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

                        if (data.status == "success") {

                            setVisible("#poweron-server", false);
                            setVisible("#reboot-server", true);
                            setVisible("#poweroff-server", true);
                            setVisible("#cycle-server", true);
                        }
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $('#poweron-server').click(function () {
        $("#instance-view-poweron-confirm-form").dialog("open");
    });
});