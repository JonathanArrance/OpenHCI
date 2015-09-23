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
        actions = $('#widget-actions'),
        progressbar = $('#instance-progressbar');

    $("#instance-view-poweroff-confirm-form").dialog({
        autoOpen: false,
        height: 125,
        width: 235,
        modal: true,
        buttons: {
            "Confirm": function () {

                messages.showMessage('notice', 'Powering Off');

                // Hide other actions
                actions.slideUp();

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                $.getJSON('/server/' + PROJECT_ID + '/' + SERVER_ID + '/power_off_server/')
                    .done(function (data) {

                        if (data.status == "error") {

                            messages.showMessage('error', data.message);
                        }

                        if (data.status == "success") {

                            messages.showMessage('success', data.message);
                            emptyAndAppend(status, "SHUTOFF");
                        }
                    })
                    .fail(function () {

                        messages.showMessage('error', 'Server Fault');
                        emptyAndAppend(status, "ERROR");
                    })
                    .always(function (data) {

                        actions.slideDown();
                        setVisible(progressbar, false);

                        if (data.status == "success") {
                            setVisible("#poweron-server", true);
                            setVisible("#reboot-server", false);
                            setVisible("#poweroff-server", false);
                            setVisible("#cycle-server", false);
                        }
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $('#poweroff-server').click(function () {
        $("#instance-view-poweroff-confirm-form").dialog("open");
    });
});