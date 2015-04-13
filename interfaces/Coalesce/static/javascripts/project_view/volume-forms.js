$(function () {

    // Widget Elements
    var progressbar = $("#vol_progressbar"),
        table = $("#volume_list"),
        placeholder =
            '<tr id="volume_placeholder"><td><p><i>This project has no volumes</i></p></td><td></td><td></td>/tr>';

    // --- Create ---

    $(function () {

        // Form Elements
        var volume_name = $("#volume_name"),
            volume_size = $("#volume_size"),
            description = $("#description"),
            volume_type = $("#volume_type"),
            allFields = $([]).add(volume_name).add(volume_size).add(description).add(volume_type);

        // Open modal form when create-volume button is clicked
        $(document).on("click", "#create-volume", function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#volume-dialog-form").dialog("open");
        });

        $("#volume-dialog-form").dialog({
            autoOpen: false,
            height: 445,
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

                    // Validate form inputs
                    var isValid =
                        checkLength(volume_name, "Volume Name", 3, 16) &&
                        checkDuplicateName(volume_name, volumes) &&
                        checkSize(volume_size, "Volume Size must be greater than 0.", 1, 0) &&
                        checkStorage(volume_size) &&
                        checkLength(description, "Description", 1, 16);

                    if (isValid) {

                        // Confirmed Selections
                        var confVolume = volume_name.val(),
                            confSize = volume_size.val(),
                            confDesc = description.val(),
                            confType = volume_type.val();

                        if (confDesc == '') {
                            confDesc = 'none';
                        }

                        message.showMessage('notice', 'Creating new volume ' + volume_name.val());

                        // Disable widget view links and hide create button
                        disableLinks(true);
                        setVisible("#create-volume", false);

                        // Initialize progressbar and make it visible if hidden
                        $(progressbar).progressbar({value: false});
                        disableProgressbar(progressbar, "volumes", false);

                        $.getJSON('/create_volume/' + confVolume + '/' + confSize + '/' + confDesc + '/' + confType + '/' + PROJECT_ID + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    message.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    message.showMessage('success', data.message);

                                    // Initialize empty string for new volume row
                                    var newRow =
                                        '<tr id="' + data.volume_id + '" class="' + data.volume_size + '">' +
                                        '<td id="' + data.volume_id + '-name-cell">' +
                                        '<a href="/projects/' + PROJECT_ID + '/volumes/' + data.volume_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                        '<span id="' + data.volume_id + '-name-text">' + data.volume_name + '</span>' + '</a></td>' +
                                        '<td id="' + data.volume_id + '-attached-cell"><span id="' + data.volume_id + '-attached-placeholder">No Attached Instance</span></td>' +
                                        '<td id="' + data.volume_id + '-actions-cell"><a href="#" class="attach-volume">attach</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="clone-volume">clone</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="revert-volume">revert</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a></td></tr>';

                                    // Check to see if this is the first volume to be generated, if so remove placeholder and reveal create-snapshot buttons
                                    var rowCount = $("#volume_list tr").length;
                                    if (rowCount <= 2) {
                                        $("#volume_placeholder").remove().fadeOut();
                                        setVisible('#create-snapshot', true);
                                    }

                                    // Append new row to volume-list
                                    table.append(newRow).fadeIn();

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

                                message.showMessage('error', 'Server Fault');	// Flag server fault message
                            })
                            .always(function () {

                                // Reset interface
                                disableProgressbar(progressbar, "volumes", true);
                                setVisible("#create-volume", true);
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
            volume,
            targetRow;

        $(document).on('click', '.delete-volume', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            volume = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#volume-delete-confirm-form > p > span.volume-name').empty().append($(volume).text());

            // Check if volume has dependent snap shots. If so, do not allow the user to delete the volume
            var count = 0;
            for (var snapshot in snapshots.items) {
                var vol = snapshots.getItem(snapshot).volumeId;
                if (vol == id) {
                    count++;
                }
            }
            if (count > 0) {
                message.showMessage('error', "Cannot delete this volume because it has " + count + " dependent snapshots.")
            } else {
                $('#volume-delete-confirm-form').dialog("open");
            }
        });

        $("#volume-delete-confirm-form").dialog({
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

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confVol = $(volume).text();

                    message.showMessage('notice', "Deleting " + confVol + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("delete-volume", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "volumes", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/delete_volume/' + confId + '/' + PROJECT_ID + '/')
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

                                // Remove volume
                                volumes.removeItem(confId);
                                snapshotVolumes.removeItem(confId);

                                // Update select
                                refreshSelect($("#snap_volume"), snapshotVolumes);

                                // Update usedStorage
                                updateUsedStorage();
                                updateStorageBar();

                                // If last row, append placeholder
                                var rowCount = $('#volume_list tr').length;
                                if (rowCount < 2) {
                                    $(table).append(placeholder).fadeIn();
                                    setVisible('#create-snapshot', false);
                                }
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
                            disableProgressbar(progressbar, "volumes", true);
                            disableLinks(false);
                            disableActions("delete-volume", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Clone ---

    $(function () {

        // Form Elements
        var volume_name = $("#clone_volume_name"),
            description = $("#description"),
            allFields = $([]).add(volume_name).add(description);

        // Local Variables
        var id,
            volume,
            targetRow;

        $(document).on('click', '.clone-volume', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            volume = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#volume-clone-form > p > span.volume-name').empty().append($(volume).text());

            $('#volume-clone-form').dialog("open");
        });

        $("#volume-clone-form").dialog({
            autoOpen: false,
            height: 250,
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

                    // Confirmed Selections
                    var confId = id,
                        confVol = volume_name.val(),
                        confDesc = description.val();

                    if (confVol == '') {
                        confVol = 'none';
                    }

                    if (confDesc == '') {
                        confDesc = 'none';
                    }

                    message.showMessage('notice', "Cloning " + $(volume).text() + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("clone-volume", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "volumes", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/create_vol_clone/' + PROJECT_ID + '/' + confId + '/' + confVol + '/' + confDesc + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', "Volume " + confVol + " cloned from volume " + $(volume).text() + ".");

                                // Initialize empty string for new volume row
                                var newRow =
                                    '<tr id="' + data.volume_id + '"><td id="' + data.volume_id + '-name-cell">' +
                                    '<a href="/projects/' + PROJECT_ID + '/volumes/' + data.volume_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.volume_id + '-name-text">' + data.volume_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.volume_id + '-attached-cell"><span id="' + data.volume_id + '-attached-placeholder">No Attached Instance</span></td>' +
                                    '<td id="' + data.volume_id + '-actions-cell"><a href="#" class="attach-volume">attach</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="clone-volume">clone</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="revert-volume">revert</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a></td></tr>';

                                // Check to see if this is the first volume to be generated, if so remove placeholder and reveal create-snapshot buttons
                                var rowCount = $("#volume_list tr").length;
                                if (rowCount <= 2) {
                                    $("#volume_placeholder").remove().fadeOut();
                                    setVisible('#create-snapshot', true);
                                }

                                // Append new row to volume-list
                                table.append(newRow).fadeIn();

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

                            // Restore actions cell html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "volumes", true);
                            disableLinks(false);
                            disableActions("clone-volume", false);
                            resetUiValidation(allFields);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Attach ---

    $(function () {

        // Local Variables
        var id,
            volume,
            targetRow;

        $(document).on('click', '.attach-volume', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            volume = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#volume-attach-dialog-form > p > span.volume-name').empty().append($(volume).text());

            $('#volume-attach-dialog-form').dialog("open");
        });

        $("#volume-attach-dialog-form").dialog({
            autoOpen: false,
            height: 225,
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
                "Attach Volume": function () {

                    // Form elements
                    var instance = $("#instance");

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confVol = $(volume).text(),
                        confInstance = instanceOpts.items[instance.val()].value,
                        confInstanceName = instanceOpts.items[confInstance].option;

                    message.showMessage('notice', 'Attaching ' + confVol + ' to ' + confInstanceName + '.');

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("attach-volume", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "volumes", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/attach_volume/' + PROJECT_ID + '/' + confInstance + '/' + confId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Update row
                                var targetAttached = document.getElementById(confId + "-attached-cell");

                                $(actionsCell).empty().fadeOut();
                                $(targetAttached).empty().fadeOut();

                                var newActions =
                                    '<a href="#" class="detach-volume">detach</a><span class="volume-actions-pipe"> | </span><a href="#" class="clone-volume">clone</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="revert-volume">revert</a>';

                                $(actionsCell).append(newActions).fadeIn();
                                $(targetAttached).append(confInstanceName).fadeIn();

                                confRow.addClass("volume-attached");
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
                            disableProgressbar(progressbar, "volumes", true);
                            disableLinks(false);
                            disableActions("attach-volume", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Detach ---

    $(function () {

        // Local Variables
        var id,
            volume,
            targetRow;

        // Form elements
        var instance = $("#instance");

        $(document).on('click', '.detach-volume', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = targetRow.attr("id");
            volume = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#volume-detach-confirm-form > p > span.volume-name').empty().append($(volume).text());

            $('#volume-detach-confirm-form').dialog("open");
        });

        $("#volume-detach-confirm-form").dialog({
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
                "Detach Volume": function () {

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confVol = $(volume).text(),
                        confInstance = instance.val(),
                        confInstanceName = instanceOpts.items[confInstance].option;

                    message.showMessage('notice', 'Detaching ' + confVol + ' from ' + confInstanceName + '.');

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("detach-volume", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "volumes", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/detach_volume/' + PROJECT_ID + '/' + confId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Update row
                                var targetAttached = document.getElementById(confId + "-attached-cell");

                                $(actionsCell).empty().fadeOut();
                                $(targetAttached).empty().fadeOut();

                                var newActions =
                                    '<a href="#" class="attach-volume">attach</a><span class="volume-actions-pipe"> | </span>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="clone-volume">clone</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="revert-volume">revert</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a>';

                                $(actionsCell).append(newActions).fadeIn();
                                $(targetAttached).append("No Attached Instance").fadeIn();

                                confRow.removeClass("volume-attached");
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
                            disableProgressbar(progressbar, "volumes", true);
                            disableLinks(false);
                            disableActions("detach-volume", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Revert From Snapshot ---

    $(function () {

        // Form Elements
        var snapshot = $("#revert_snapshot_name"),
            name = $("#revert_volume_name"),
            allFields = $([]).add(snapshot);

        // Local Variables
        var id,
            volume,
            targetRow,
            attached;

        $(document).on('click', '.revert-volume', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that
            // element and use that to get the name-text
            targetRow = $(this).parent().parent();
            attached = !!targetRow.hasClass("volume-attached");
            id = $(targetRow).attr("id");
            volume = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#volume-revert-form > p > span.volume-name').empty().append($(volume).text());
            updateRevertVolumeSnapshots(id);

            $('#volume-revert-form').dialog("open");
        });

        $("#volume-revert-form").dialog({
            autoOpen: false,
            height: 250,
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

                    // Remove UI validation flags
                    clearUiValidation(allFields);

                    // Validate form inputs
                    var isValid =
                        checkLength(name, "Volume Name", 3, 16) &&
                        checkDuplicateName(name, volumes);

                    if (isValid) {

                        // Confirmed Selections
                        var confId = id,
                            confName = name.val(),
                            confSnap = snapshot.val();

                        message.showMessage('notice', "Reverting " + $(volume).text() + ".");

                        // Store actions cell html
                        var actionsCell = document.getElementById(confId + "-actions-cell");
                        var actionsHtml = actionsCell.innerHTML;

                        // Disable widget view links and instance actions
                        disableLinks(true);
                        disableActions("revert-volume", true);

                        // Initialize progressbar and make it visible
                        $(progressbar).progressbar({value: false});
                        disableProgressbar(progressbar, "volumes", false);

                        // Create loader
                        var loaderId = confId + '-loader';
                        var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                        // Clear clicked action link and replace with loader
                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(loaderHtml).fadeIn();

                        $.getJSON('/revert_volume_snapshot/' + PROJECT_ID + '/' + confId + '/' + confName + '/' + confSnap + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    message.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    message.showMessage('success', data.message);

                                    // Initialize empty string for new volume row
                                    var newRow =
                                        '<tr id="' + data.volume_info.volume_id + '" class="';
                                    if (attached) {
                                        newRow += "volume-attached"
                                    }
                                    newRow +=
                                        '"><td id="' + data.volume_info.volume_id + '-name-cell">' +
                                        '<a href="/projects/' + PROJECT_ID + '/volumes/' + data.volume_info.volume_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                        '<span id="' + data.volume_info.volume_id + '-name-text">' + data.volume_info.volume_name + '</span>' + '</a></td>' +
                                        '<td id="' + data.volume_info.volume_id + '-attached-cell"><span id="' + data.volume_info.volume_id + '-attached-placeholder">';
                                    if (attached) {
                                        newRow += instances.items[data.attach_info.instance_id].name
                                    } else {
                                        newRow += "No Attached Instances"
                                    }
                                    newRow += '</span></td><td id="' + data.volume_info.volume_id + '-actions-cell">';
                                    if (!attached) {
                                        newRow += '<a href="#" class="attach-volume">attach</a>';
                                    } else {
                                        newRow += '<a href="#" class="detach-volume">detach</a>';
                                    }
                                    newRow +=
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="clone-volume">clone</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="revert-volume">revert</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a></td></tr>';

                                    // Check to see if this is the first volume to be generated, if so remove placeholder and reveal create-snapshot buttons
                                    var rowCount = $("#volume_list tr").length;
                                    if (rowCount <= 2) {
                                        $("#volume_placeholder").remove().fadeOut();
                                        setVisible('#create-snapshot', true);
                                    }

                                    // Append new row to volume-list
                                    table.append(newRow).fadeIn();

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

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();

                                // Hide progressbar and enable widget view links
                                disableProgressbar(progressbar, "volumes", true);
                                disableLinks(false);
                                disableActions("revert-volume", false);
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