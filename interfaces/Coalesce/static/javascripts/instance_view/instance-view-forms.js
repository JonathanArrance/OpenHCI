$(function () {
    // Widget Elements
    var instProgressbar = $("#instance_progressbar"),
        snapProgressbar = $("#snapshot_progressbar"),
        actions = $('#widget-actions');

    // --- Create Instance Snapshot ---

    $(function () {

        // Form Elements
        var name = $("#instance_snap_name"),
            description = $("#instance_snap_desc"),
            allFields = $([]).add(name).add(description);

        $("#create-instance-snapshot").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#instance-snapshot-dialog-form").dialog("open");
        });

        $("#instance-snapshot-dialog-form").dialog({
            autoOpen: false,
            height: 375,
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
                        checkLength(name, "Snapshot Name", 0, 16) &&
                        checkLength(description, "Snapshot Description", 0, 80);

                    if (isValid) {

                        // Confirmed Selections
                        var confName = name.val(),
                            confDesc = description.val();

                        if (confName == '') {
                            confName = 'none';
                        }

                        if (confDesc == '') {
                            confDesc = 'none';
                        }

                        message.showMessage('notice', 'Creating new instance snapshot ' + confName);

                        // Disable widget view links and hide create button
                        disableLinks(true);
                        setVisible("#create-instance-snapshot", false);

                        // Initialize progressbar and make it visible if hidden
                        $(snapProgressbar).progressbar({value: false});
                        disableProgressbar(snapProgressbar, "snpashots", false);

                        $.getJSON('/create_instance_snapshot/' + PROJECT_ID + '/' + SERVER_ID + '/' + confName + '/' + confDesc + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    message.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    message.showMessage('success', data.message);

                                    // Initialize empty string for new snapshot row
                                    var newRow =
                                        '<tr id="' + data.snapshot_id + '">' +
                                        '<td id="' + data.snapshot_id + '-name-cell">' + data.snapshot_name + '</td>' +
                                        '<td id="' + data.snapshot_id + '-id-cell">' + data.snapshot_id + '</td>' +
                                        '<td id="' + data.snapshot_id + '-actions-cell"><a href="#" class="delete-snapshot">delete</a></td></tr>';

                                    // Append new row
                                    $("#snapshot_list").append(newRow).fadeIn();

                                    // Check to see if this is the first network to be generated, if so remove placeholder
                                    var rowCount = $("#snapshot_list tr").length;
                                    if (rowCount > 2) {
                                        $("#snapshot_placeholder").remove().fadeOut();
                                    }

                                    // Update Selects
                                    instanceSnaps.setItem(data.snapshot_id, { name: data.snapshot_name, instanceId: data.instance_id, instanceName: SERVER_NAME });
                                    updateRevertInstanceSnapshots();
                                }

                            })
                            .fail(function () {

                                message.showMessage('error', 'Server Fault');	// Flag server fault message
                            })
                            .always(function () {

                                // Reset interface
                                disableProgressbar(snapProgressbar, "snapshots", true);
                                setVisible("#create-instance-snapshot", true);
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
    });

    // --- Revert from Snapshot ---

    $(function () {

        // Form Elements
        var snapName = $("#instance_snapshot_name"),
            allFields = $([]).add(snapName);

        $(document).on('click', '#revert-server', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Add instance-name-text to confirm-form
            $('div#instance-revert-form > p > span.instance-name').empty().append(SERVER_NAME);
            updateRevertInstanceSnapshots();

            $("#instance-revert-form").dialog("open");
        });

        $("#instance-revert-form").dialog({
            autoOpen: false,
            height: 235,
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
                "Revert Instance": function () {

                    // Confirmed Selections
                    var confSnap = snapName.val();

                    // Remove UI validation flags
                    clearUiValidation(allFields);

                    // Validate form inputs
                    message.showMessage('notice', 'Reverting Instance ' + SERVER_NAME);

                    // Initialize progressbar and make it visible if hidden
                    $(instProgressbar).progressbar({value: false});
                    disableProgressbar(instProgressbar, "instances", false);

                    actions.slideUp();

                    $.getJSON('/revert_instance_snapshot/' + PROJECT_ID + '/' + SERVER_ID + '/' + confSnap + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                window.location.assign(STATIC_URL + '/' + PROJECT_ID + '/' + SERVER_ID + '/instance_view/');
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            // Reset interface
                            disableProgressbar(instProgressbar, "instances", true);
                            resetUiValidation(allFields);
                            actions.slideDown();
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {

                // Reset form validation
                resetUiValidation(allFields);
            }
        });
    });

    function updateRevertInstanceSnapshots() {

        var select = $("#instance_snapshot_name");
        select.empty();

        for (var snap in instanceSnaps.items) {
            select.append(
                    '<option value="' + snap + '">' + instanceSnaps.items[snap].name + '</option>'
            );
        }
    }
});