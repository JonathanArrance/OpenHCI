$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Form Elements
    var volume_name = $("#volume_name"),
        volume_size = $("#volume_size"),
        volume_available_storage_bar = $(".volume-available-storage-bar"),
        volume_available_storage_label = $(".volume-available-storage-label"),
        description = $("#description"),
        volume_type = $("#volume_type"),
        allFields = $([]).add(volume_name).add(volume_size).add(description).add(volume_type),
        tips = $(".validateTips");

    // Widget Elements
    var progressbar = $("#vol_progressbar"),
        createButton = $("#create-volume"),
        deleteButton = $("#delete-volume"),
        table = $("#volume_list");


    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#volume-dialog-form").dialog({
        autoOpen: false,
        height: 445,
        width: 200,
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

                var bValid = true;

                allFields.removeClass("ui-state-error");
                $(".error").fadeOut().remove();

                bValid =
                    bValid &&
                    checkLength(tips, volume_name, "Volume Name", 3, 16) &&
                    checkLength(tips, description, "Description", 1, 16) &&
                    checkStorage(tips, volume_size);

                if (bValid) {

                    message.showMessage('notice', 'Creating new volume ' + volume_name.val());

                    setVisible(createButton, false);
                    setVisible(deleteButton, false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    setVisible(progressbar, true);

                    $.getJSON('/create_volume/' + volume_name.val() + '/' + volume_size.val() + '/' + description.val() + '/' + volume_type.val() + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {
                                message.showMessage('error', data.message);
                            }
                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new volume row
                                var newRow = '';
                                newRow +=
                                    '<tr id="' + data.volume_id + '" class="' + data.volume_size + '">' +
                                    '<td id="' + data.volume_id + '-name-cell">' +
                                    '<a href="/projects/' + PROJECT_ID + '/volumes/' + data.volume_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.volume_id + '-name-text">' + data.volume_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.volume_id + '-attached-cell"><span id="' + data.volume_id + '-attached-placeholder">No Attached Instances</span></td>' +
                                    '<td id="' + data.volume_id + '-actions-cell"><a href="#" class="attach-instance">attach</a></td>' + '</tr>';

                                // Check to see if this is the first volume to be generated, if so remove placeholder and reveal delete-volume button
                                var rowCount = $("#volume_list tr").length;
                                if (rowCount <= 2) {
                                    $("#volume_placeholder").remove().fadeOut();
                                }

                                // Append new row to volume-list
                                table.append(newRow).fadeIn();

                                // Append new option to delete-volume select menu
                                var deleteSelect = 'div#volume-delete-dialog-form > form > fieldset > select#volume';
                                var newOption = '<option value ="' + data.volume_id + '">' + data.volume_name + '</option>';
                                $(deleteSelect).append(newOption);
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');	// Flag server fault message
                        })
                        .always(function() {

                            setVisible(progressbar, false);
                            setVisible(createButton, true);
                            setVisible(deleteButton, true);
                            disableLinks(false);
                        });

                    $(this).dialog("close");

                    allFields.val("").removeClass("ui-state-error");
                    $(".error").fadeOut().remove();
                }
            }
        },
        close: function () {
            allFields.val("").removeClass("ui-state-error");
            $(".error").fadeOut().remove();
        }
    });

    // Open modal form when create-volume button is clicked
    $(document).on("click", "#create-volume", function () {

        var percent = 0;

        volume_available_storage_bar.progressbar({value: 0});
        volume_available_storage_label.empty();
        volume_available_storage_label.append("Calculating ....");

        $.getJSON('/projects/' + PROJECT_ID + '/get_project_quota/')
            .done(function (data) {

                if (data.status == "error") {

                    message.showMessage('error', data.message);
                    getUsedStorage("#volume_list tr");
                    percent = (usedStorage / totalStorage) * 100;

                    volume_available_storage_bar.progressbar({value: percent});
                    volume_available_storage_label.empty();
                    volume_available_storage_label.append(usedStorage + "/" + totalStorage);
                }
                if (data.status == "success") {

                    totalStorage = data.gigabytes;
                    getUsedStorage("#volume_list tr");
                    percent = (usedStorage / totalStorage) * 100;

                    volume_available_storage_bar.progressbar({value: percent});
                    volume_available_storage_label.empty();
                    volume_available_storage_label.append(usedStorage + "/" + totalStorage);
                }
            })
            .fail(function () {

                message.showMessage('error', "Server Fault");
                getUsedStorage("#volume_list tr");
                percent = (usedStorage / totalStorage) * 100;

                volume_available_storage_bar.progressbar({value: percent});
                volume_available_storage_label.empty();
                volume_available_storage_label.append(usedStorage + "/" + totalStorage);
            });

        $("#volume-dialog-form").dialog("open");
    });
});


