$(function () {

    var csrftoken = getCookie('csrftoken');
    var volume = $("#volume");
    var placeholder = '<tr id="volume_placeholder"><td><p><i>This project has no volumes</i></p></td><td></td><td></td>/tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $("#volume-delete-dialog-form").dialog({
        autoOpen: false,
        height: 250,
        width: 350,
        modal: true,
        buttons: {
            "Confirm": function () {

                message.showMessage('notice', 'Deleting Volume');

                setVisible('#create-volume', false);
                setVisible('#delete-volume', false);
                disableLinks(true);

                // Initialize progressbar and make it visible if hidden
                $('#vol_progressbar').progressbar({value: false});
                setVisible('#vol_progressbar', true);

                $.getJSON('/delete_volume/' + volume.val() + '/' + PROJECT_ID + '/')
                    .success(function (data) {

                        if (data.status == 'error') {
                            message.showMessage('error', data.message);
                        }
                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Remove volume row from volume_list
                            var targetRow = '#' + volume.val();
                            $('#volume_list').find(targetRow).fadeOut().remove();

                            // Remove volume from delete-volume select menu
                            var targetOption = 'select#volume option[value=' + volume.val() + ']';
                            $(targetOption).remove();
                        }

                        setVisible('#vol_progressbar', false);
                        setVisible('#create-volume', true);

                        // If last volume, add placeholder and reveal delete-volume
                        var rowCount = $('#volume_list tr').length;
                        if (rowCount < 2) {
                            $('#volume_list').append(placeholder).fadeIn();
                        } else {
                            setVisible('#delete-volume', true);
                        }

                        disableLinks(false);
                    })
                    .error(function () {

                        message.showMessage('error', 'Server Fault');

                        setVisible('#vol_progressbar', false);
                        setVisible('#create-volume', true);
                        setVisible('#delete-volume', true);
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

    $("#delete-volume").click(function () {
        $("#volume-delete-dialog-form").dialog("open");
    });

    // If placeholder exists, hide delete-instance
    $(document).ready(function () {
        if ($('#volume_placeholder').length) {
            setVisible('#delete-volume', false)
        }
    });
});
