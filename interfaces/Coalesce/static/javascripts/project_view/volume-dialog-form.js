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

    // Form Elements
    var volume_name = $("#volume_name"),
        volume_size = $("#volume_size"),
        description = $("#description"),
        volume_type = $("#volume_type"),
        allFields = $([]).add(volume_name).add(volume_size).add(description).add(volume_type);

    // Widget Elements
    var progressbar = $("#vol_progressbar"),
        createButton = $("#create-volume"),
        table = $("#volume_list");

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

                    message.showMessage('notice', 'Creating new volume ' + volume_name.val());

                    // Disable widget view links and hide create button
                    disableLinks(true);
                    setVisible(createButton, false);

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
                                    '<td id="' + data.volume_id + '-attached-cell"><span id="' + data.volume_id + '-attached-placeholder">No Attached Instances</span></td>' +
                                    '<td id="' + data.volume_id + '-actions-cell"><a href="#" class="attach-volume">attach</a>' +
                                    '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a></td></tr>';

                                // Check to see if this is the first volume to be generated, if so remove placeholder and reveal delete-volume button
                                var rowCount = $("#volume_list tr").length;
                                if (rowCount <= 2) {
                                    $("#volume_placeholder").remove().fadeOut();
                                }

                                // Append new row to volume-list
                                table.append(newRow).fadeIn();

                                // Add to volumes
                                volumes.setItem(data.volume_id, { size: confSize });

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

    // Open modal form when create-volume button is clicked
    $(document).on("click", "#create-volume", function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        $("#volume-dialog-form").dialog("open");
    });
});


