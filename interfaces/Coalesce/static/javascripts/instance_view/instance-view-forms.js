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
                        checkLength(name, "Snapshot Name", 0, standardStringMax) &&
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

                        messages.showMessage('notice', 'Creating new instance snapshot.');

                        // Disable widget view links and hide create button
                        disableLinks(true);
                        setVisible("#create-instance-snapshot", false);

                        // Initialize progressbar and make it visible if hidden
                        $(snapProgressbar).progressbar({value: false});
                        disableProgressbar(snapProgressbar, "snapshots", false);

                        $.getJSON('/create_instance_snapshot/' + PROJECT_ID + '/' + SERVER_ID + '/' + confName + '/' + confDesc + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    messages.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    messages.showMessage('success', data.message);

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
                                    instanceSnaps.setItem(data.snapshot_id, {
                                        name: data.snapshot_name,
                                        instanceId: data.instance_id,
                                        instanceName: SERVER_NAME
                                    });
                                    updateRevertInstanceSnapshots();
                                }

                            })
                            .fail(function () {

                                messages.showMessage('error', 'Server Fault');	// Flag server fault message
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
                    messages.showMessage('notice', 'Reverting Instance ' + SERVER_NAME);

                    // Initialize progressbar and make it visible if hidden
                    $(instProgressbar).progressbar({value: false});
                    disableProgressbar(instProgressbar, "instances", false);

                    actions.slideUp();

                    $.getJSON('/revert_instance_snapshot/' + PROJECT_ID + '/' + SERVER_ID + '/' + confSnap + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                messages.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

                                window.location.assign(STATIC_URL + '/' + PROJECT_ID + '/' + SERVER_ID + '/instance_view/');
                            }
                        })
                        .fail(function () {

                            messages.showMessage('error', 'Server Fault');
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

    // --- Delete ---

    $(function () {
        $(document).on('click', '.delete-snapshot', function (event) {
            // Prevent scrolling to top of page on click
            event.preventDefault();
            // Get target row element, get id from that element and use that to get the name-text
            var targetRow = $(this).parent().parent(),
                id = $(targetRow).attr("id"),
                snap = $(document.getElementById(id + "-name-cell")).html();

            // Create form
            $("<div></div>").prop("id", "instance-snapshot-delete-confirm-form").prop("title", "Delete Snapshot")
                .append($("<p></p>").css("text-align", "center").html("Delete " + snap + "?"))
                .dialog({
                    autoOpen: true,
                    height: 125,
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
                        "Confirm": function () {

                            // Delete instance
                            deleteInstanceSnapshot(id, snap, targetRow);

                            // Close Dialog form
                            $(this).remove();
                        }
                    }
                });

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

    function deleteInstanceSnapshot(id, name, row) {
        // Confirmed Selections
        var confId = id,
            confSnap = name,
            confRow = row;
        // Show toast message
        messages.showMessage('notice', "Deleting " + confSnap + ".");
        // Store actions cell html
        var actionsCell = $(document.getElementById(confId + "-actions-cell"));
        var actionsHtml = actionsCell.html();
        // Initialize progressbar and make it visible if hidden
        $(snapProgressbar).progressbar({value: false});
        disableProgressbar(snapProgressbar, "snapshots", false);
        // Disable widget view links and instance actions
        disableLinks(true);
        disableActions("delete-snapshot", true);
        // Clear clicked action link and replace with loader
        actionsCell.empty()
            .append($("<div></div>").prop("id", confId + '-loader').prop("class", "ajax-loader").fadeIn());
        $.getJSON('/server/' + confId + '/delete_instance_snapshot/')
            .done(function (data) {
                if (data.status == 'error') {
                    // Show toast message
                    messages.showMessage('error', data.message);
                    // Restore actions cell html
                    actionsCell.empty()
                        .append(actionsHtml.fadeIn());
                }
                if (data.status == 'success') {
                    // Show toast message
                    messages.showMessage('success', data.message);
                    // Remove row
                    confRow.fadeOut().remove();
                    // Remove snapshot
                    instanceSnaps.removeItem(confId);
                    // If last row, append placeholder
                    if ($('#snapshot_list tr').length < 2) {
                        $("<tr></tr>").prop("id", "snapshot_placeholder")
                            .append($("<td></td>")
                                .append($("<p></p>")
                                    .append($("<i></i>").html("This instance has no snapshots"))))
                            .append($("<td></td>"))
                            .append($("<td></td>"))
                            .appendTo($("#snapshot_list")).fadeIn();
                    }
                }
            })
            .fail(function () {
                messages.showMessage('error', 'Server Fault');
                // Restore actions cell html
                actionsCell.empty()
                    .append(actionsHtml.fadeIn());
            })
            .always(function () {
                // Hide progressbar and enable widget view links
                disableProgressbar(snapProgressbar, "snapshots", true);
                checkAssignFip();
                disableActions("delete-snapshot", false);
                disableLinks(false);
            });
    }
});

