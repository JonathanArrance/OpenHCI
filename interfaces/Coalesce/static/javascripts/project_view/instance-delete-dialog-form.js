$(function () {

    var csrftoken = getCookie('csrftoken');
    var instance = $('#instance');
    var placeholder = '<tr id="instance_placeholder"><td><p><i>This project has no instances</i></p></td><td></td><td></td><td></td></tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#instance-delete-dialog-form").dialog({
        autoOpen: false,
        height: 250,
        width: 350,
        modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position: {
            my: "center",
            at: "center",
            of: $('#page-content')
        },
        buttons: {
            "Confirm": function () {

                message.showMessage('notice', 'Deleting Instance');
                var confirmedInstance = $(instance).find("option:selected");

                setVisible('#create-instance', false);
                setVisible('#delete-instance', false);
                disableLinks(true);

                // Initialize progressbar and make it visible if hidden
                $('#instance_progressbar').progressbar({value: false});
                setVisible('#instance_progressbar', true);

                $.getJSON('/server/' + PROJECT_ID + '/' + confirmedInstance.val() + '/delete_server/')
                    .success(function (data) {

                        if (data.status == 'error') {
                            message.showMessage('error', data.message);
                        }
                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Remove instance row from instance_list
                            var targetRow = '#' + confirmedInstance.val();
                            $('#instance_list').find(targetRow).fadeOut().remove();

                            // Remove instance from delete-instance select menu
                            var deleteSelect = 'div#instance-delete-dialog-form > form > fieldset > select#instance option[value=' + confirmedInstance.val() + ']';
                            $(deleteSelect).remove();

                            // Remove instance from attach-volume select menu
                            var attachSelect = 'div#volume-attach-dialog-form > form  > fieldset > select#instance option[value=' + confirmedInstance.val() + ']';
                            $(attachSelect).remove();

                            // Remove instance from assign-fip select menu
                            var assignSelect = 'div#fip-assign-dialog-form > form > fieldset > select#assign_instance option[value=' + confirmedInstance.val() + ']';
                            $(assignSelect).remove();

                            for (var i = 0; i < data.vols.length; i++) {
                                var volAttachedCell = document.getElementById(data.vols[i] + '-attached-cell');
                                $(volAttachedCell).empty().fadeOut();
                                var newAttached = '<span id="' + data.vols[i] + '-attached-placeholder">No Attached Instance</span>';
                                $(volAttachedCell).append(newAttached).fadeIn();

                                var volActionsCell = document.getElementById(data.vols[i] + '-actions-cell');
                                $(volActionsCell).empty().fadeOut();
                                var newVolAction = '<a href="#" class="attach-instance">attach</a>';
                                $(volActionsCell).append(newVolAction).fadeIn();
                            }

                            for (var j = 0; j < data.floating_ip.length; j++) {
                                var ipInstanceCell = document.getElementById(data.floating_ip[j] + '-instance-cell');
                                $(ipInstanceCell).empty().fadeOut();
                                var newInstance = '<span id="' + data.floating_ip[j] + '-instance-name">None</span>';
                                $(ipInstanceCell).append(newInstance).fadeIn();

                                var ipActionsCell = document.getElementById(data.floating_ip[j] + '-actions-cell');
                                $(ipActionsCell).empty().fadeOut();
                                var newIpAction = '<a id="' + data.floating_ip[j] + '" class="deallocate_ip" href="#">deallocate</a>';
                                $(ipActionsCell).append(newIpAction).fadeIn();
                            }

                            setVisible('#instance_progressbar', false);
                            setVisible('#create-instance', true);

                            // If last instance, add placeholder and hide delete-instance
                            var rowCount = $('#instance_list tr').length;
                            if (rowCount < 2) {
                                $('#instance_list').append(placeholder).fadeIn();
                            } else {
                                setVisible('#delete-instance', true);
                            }

                            disableLinks(false);
                        }
                    })
                    .error(function () {

                        message.showMessage('error', 'Server Fault');

                        setVisible('#instance_progressbar', false);
                        setVisible('#create-instance', true);
                        setVisible('#delete-instance', true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
        }
    })

    $("#delete-instance").click(function () {
        $("#instance-delete-dialog-form").dialog("open");
    });

    // If placeholder exists, hide delete-instance
    $(document).ready(function () {
        if ($('#instance_placeholder').length) {
            setVisible('#delete-instance', false)
        }
    });
});
