$(function () {

    // CSRF Protection
    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Dialog Form Elements
    var name = $("#snap_name"),
        volume = $("#snap_volume"),
        description = $("#snap_desc"),
        allFields = $([]).add(name).add(volume).add(description);

    // Widget Elements
    var progressbar = $("#snapshot_progressbar"),
        createButton = $("#create-snapshot"),
        table = $("#snapshot_list");


    $("#snapshot-dialog-form").dialog({
        autoOpen: false,
        height: 350,
        width: 235,
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
            "Create Snapshot": function () {

                // Remove UI validation flags
                clearUiValidation(allFields);

                var isValid =
                    checkLength(name, "Snapshot Name", 3, 16) &&
                    checkLength(description, "Snapshot Name", 1, 80);

                if (isValid) {

                    // Confirmed Selections
                    var confName = name.val(),
                        confVolume = volume.val(),
                        confDescription = description.val();

                    message.showMessage('notice', 'Creating new snapshot ' + confName);

                    // Disable widget view links and hide create button
                    disableLinks(true);
                    setVisible(createButton, false);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "snapshots", false);

                    $.getJSON('/create_snapshot/' + PROJECT_ID + '/' + confName + '/' + confVolume + '/' + confDescription + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new snapshot row
                                var newRow =
                                    '<tr id="' + data.snapshot_id + '">' +
                                    '<td id="' + data.snapshot_id + '-name-cell">' +
                                    '<a href="/snapshot/' + data.snapshot_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.snapshot_id + '-name-text">' + data.snapshot_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.snapshot_id + '-volume-cell">' +
                                    '<span id="' + data.snapshot_id + '-volume-text">' + volumes.getItem(data.volume_id).name + '</span></td>' +
                                    '<td id="' + data.snapshot_id + '-actions-cell"><a href="#" class="delete-snapshot">delete</a></td>' + '</tr>';

                                // Append new row
                                table.append(newRow).fadeIn();

                                // Check to see if this is the first network to be generated, if so remove placeholder
                                var rowCount = $("#snapshot_list tr").length;
                                if (rowCount > 2) {
                                    $("#snapshot_placeholder").remove().fadeOut();
                                }

                                // Add to snapshots
                                snapshots.setItem(data.snapshot_id,
                                    { id: data.snapshot_id, name: data.snapshot_name, volumeId: data.volume_id, volumeName: volumes.getItem(data.volume_id).name });
                            }

                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');	// Flag server fault message
                        })
                        .always(function () {

                            // Reset interface
                            disableProgressbar(progressbar, "snapshots", true);
                            setVisible(createButton, true);
                            disableLinks(false);
                            resetUiValidation(allFields);
                        });

                    $(this).dialog("close");
                }
            }
        },
        close: function () {

            // Reset form validation
            resetUiValidation(allFields);
        }
    });

    $("#create-snapshot")
        .click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#snapshot-dialog-form").dialog("open");
        });

    // If volume placeholder exists, hide create-snapshot
    $(document).ready(function () {
        if ($('#volume_placeholder').length) {
            setVisible('#create-snapshot', false);
        }
    });
});
