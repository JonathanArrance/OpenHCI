$(function () {

    // Widget Elements
    var progressbar = $("#snapshot_progressbar"),
        table = $("#snapshot_list"),
        placeholder = '<tr id="snapshot_placeholder"><td><p><i>This project has no snapshots</i></p></td><td></td><td></td></tr>';

    // If volume placeholder exists, hide create-snapshot
    $(document).ready(function () {
        if ($('#volume_placeholder').length) {
            setVisible('#create-snapshot', false);
        }
    });

    // --- Create ---

    $(function () {

        // Form Elements
        var name = $("#snap_name"),
            volume = $("#snap_volume"),
            description = $("#snap_desc"),
            allFields = $([]).add(name).add(volume).add(description);

        $("#create-snapshot").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#snapshot-dialog-form").dialog("open");
        });

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
                        setVisible("#create-snapshot", false);

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
                                        '<td id="' + data.snapshot_id + '-actions-cell"><a href="#" class="delete-snapshot">delete</a>' +
                                        '<span> | </span><a href="#" class="create-volume-from-snapshot">create volume</a></td></tr>';

                                    // Append new row
                                    table.append(newRow).fadeIn();

                                    // Check to see if this is the first network to be generated, if so remove placeholder
                                    var rowCount = $("#snapshot_list tr").length;
                                    if (rowCount > 2) {
                                        $("#snapshot_placeholder").remove().fadeOut();
                                    }

                                    // Add to snapshots
                                    snapshots.setItem(data.snapshot_id,
                                        { id: data.snapshot_id, name: data.snapshot_name, volumeId: data.volume_id, volumeName: volumes.getItem(data.volume_id).name,
                                        value: data.snapshot_id, option: data.snapshot_name });

                                    // Update Select
                                    refreshSelect("#revert_snapshot_name", snapshots);
                                }

                            })
                            .fail(function () {

                                message.showMessage('error', 'Server Fault');	// Flag server fault message
                            })
                            .always(function () {

                                // Reset interface
                                disableProgressbar(progressbar, "snapshots", true);
                                setVisible("#create-snapshot", true);
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

    // --- Delete ---

    $(function () {

        // Local Variables
        var id,
            snapshot,
            targetRow;

        $(document).on('click', '.delete-snapshot', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            snapshot = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#snapshot-delete-confirm-form > p > span.snapshot-name').empty().append($(snapshot).text());

            $('#snapshot-delete-confirm-form').dialog("open");
        });

        $('#snapshot-delete-confirm-form').dialog({
            autoOpen: false,
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

                    var confId = id,
                        confSnapshot = $(snapshot).text(),
                        confRow = targetRow;

                    message.showMessage('notice', "Deleting " + confSnapshot + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("delete-snapshot", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "snapshots", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/delete_snapshot/' + PROJECT_ID + '/' + confId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Remove row
                                confRow.fadeOut().remove();

                                // If last snapshot, reveal placeholder
                                var rowCount = $('#snapshot_list tr').length;
                                if (rowCount < 2) {
                                    $(table).append(placeholder).fadeIn();
                                }

                                // Remove from snapshots
                                snapshots.removeItem(confId);
                            }

                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "snapshots", true);
                            disableLinks(false);
                            disableActions("delete-snapshot", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Create Volume From Snapshot---

    $(function () {

        // Local Variables
        var id,
            volume,
            targetRow;

        // Form Elements
        var volume_name = $("#vol_from_snap_name"),
            volume_size = $("#vol_from_snap_size"),
            allFields = $([]).add(volume_name).add(volume_size);

        $(document).on('click', '.create-volume-from-snapshot', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            volume = snapshots.items[id].volumeName;

            // Add name-text to form
            $('div#create-volume-from-snapshot-form > p > span.vol-from-snap-name').empty().append($(volume).text());

            $('#create-volume-from-snapshot-form').dialog("open");
        });

        $('#create-volume-from-snapshot-form').dialog({
            autoOpen: false,
            height: 335,
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
                "Create Volume": function () {

                    // Remove UI validation flags
                    clearUiValidation(allFields);

                    console.log(volume_name);

                    // Validate form inputs
                    var isValid =
                        checkLength(volume_name, "Volume Name", 0, 16) &&
                        checkDuplicateName(volume_name, volumes) &&
                        checkSize(volume_size, "Volume Size must be greater than 0.", 1, 0);

                    if (isValid) {

                        // Confirmed Selections
                        var confVolume = volume_name.val(),
                            confSize = volume_size.val(),
                            confId = id,
                            confClonedVolume = $(volume).text();

                        if (confVolume == '') {
                            confVolume = 'none'
                        }

                        message.showMessage('notice', "Cloning " + confClonedVolume + ".");

                        // Store actions cell html
                        var actionsCell = document.getElementById(confId + "-actions-cell");
                        var actionsHtml = actionsCell.innerHTML;

                        // Disable widget view links and instance actions
                        disableLinks(true);
                        disableActions("create-volume-from-snapshot", true);

                        // Initialize progressbar and make it visible
                        $(progressbar).progressbar({value: false});
                        disableProgressbar(progressbar, "snapshots", false);

                        // Create loader
                        var loaderId = confId + '-loader';
                        var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                        // Clear clicked action link and replace with loader
                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(loaderHtml).fadeIn();

                        $.getJSON('/create_vol_from_snapshot/' + PROJECT_ID + '/' + confId + '/' + confSize + '/' + confVolume + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    message.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    message.showMessage('success', "Volume " + confVolume + " cloned from " + confClonedVolume + ".");

                                    // Initialize empty string for new volume row
                                    var newRow =
                                        '<tr id="' + data.volume_id + '" class="' + data.volume_size + '">' +
                                        '<td id="' + data.volume_id + '-name-cell">' +
                                        '<a href="/projects/' + PROJECT_ID + '/volumes/' + data.volume_id + '/view/" class="disable-link">' +
                                        '<span id="' + data.volume_id + '-name-text">' + data.volume_name + '</span>' + '</a></td>' +
                                        '<td id="' + data.volume_id + '-attached-cell"><span id="' + data.volume_id + '-attached-placeholder">No Attached Instances</span></td>' +
                                        '<td id="' + data.volume_id + '-actions-cell"><a href="#" class="attach-volume">attach</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a></td></tr>';

                                    // Check to see if this is the first volume to be generated, if so remove placeholder and reveal create-snapshot buttons
                                    var rowCount = $("#volume_list tr").length;
                                    if (rowCount <= 2) {
                                        $("#volume_placeholder").remove().fadeOut();
                                        setVisible('#create-snapshot', true);
                                    }

                                    // Append new row to volume-list
                                    $('#volume_list').append(newRow).fadeIn();

                                    // Add to volumes
                                    volumes.setItem(data.volume_id, { size: data.volume_size, name: data.volume_name });
                                    snapshotVolumes.setItem(data.volume_id, { value: data.volume_id, option: data.volume_name });

                                    // Update select
                                    refreshSelect($("#snap_volume"), snapshotVolumes);

                                    // Update usedStorage
                                    updateUsedStorage();
                                    updateStorageBar();
                                }

                            })
                            .fail(function () {

                                message.showMessage('error', 'Server Fault');
                            })
                            .always(function () {

                                // Restore Actions html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();

                                // Hide progressbar and enable widget view links
                                disableProgressbar(progressbar, "snapshots", true);
                                disableLinks(false);
                                disableActions("create-volume-from-snapshot", false);
                                resetUiValidation(allFields);
                            });

                        $(this).dialog("close");
                    }
                }
            },
            close: function () {
            }
        });
    });
});