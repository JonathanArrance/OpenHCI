$(function () {

    var csrftoken = getCookie('csrftoken');
    var volume_name = $("#volume_name"),
        volume_size = $("#volume_size"),
        description = $("#description"),
        volume_type = $("#volume_type"),
        allFields = $([]).add(volume_name).add(volume_size).add(description).add(volume_type),
        tips = $(".validateTips");


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
        height: 475,
        width: 350,
        modal: true,
        buttons: {
            "Create a volume": function () {

                var bValid = true;
                allFields.removeClass("ui-state-error");
                $('.error').fadeOut().remove();
                bValid =
                    bValid &&
                    checkLength(tips, volume_name, "Volume Name", 3, 16) &&
                    checkLength(tips, description, "Description", 1, 16);

                console.log(description + ' ' + description.text() + ' ' + description.val());

                if (bValid) {

                    message.showMessage('notice', 'Creating new volume ' + volume_name.val());

                    setVisible('#create-volume', false);
                    setVisible('#delete-volume', false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $('#vol_progressbar').progressbar({value: false});
                    setVisible('#vol_progressbar', true);

                    $.getJSON('/create_volume/' + volume_name.val() + '/' + volume_size.val() + '/' + description.val() + '/' + volume_type.val() + '/' + PROJECT_ID + '/')
                        .success(function (data) {

                            if (data.status == 'error') {
                                message.showMessage('error', data.message);
                            }
                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // --- BEGIN html string generation
                                // Initialize empty string for new volume row
                                var newRow = '';
                                // Start row
                                newRow += '<tr id="' + data.volume_id + '">';
                                // Create name-cell
                                newRow += '<td id="' + data.volume_id + '-name-cell"><a href="/projects/' + PROJECT_ID + '/volumes/' + data.volume_id + '/view/" class="disable-link" onclick="false" style="color:#696969;"><span id="' + data.volume_id + '-name-text">' + data.volume_name + '</span></a></td>';
                                // Create attached-cell
                                newRow += '<td id="' + data.volume_id + '-attached-cell"><span id="' + data.volume_id + '-attached-placeholder">No Attached Instances</span></td>';
                                // Create actions-cell
                                newRow += '<td id="' + data.volume_id + '-actions-cell"><a href="#" class="attach-instance">attach</a></td>';
                                // End Row
                                newRow += '</tr>';
                                // --- END html string generation

                                // Check to see if this is the first volume to be generated, if so remove placeholder and reveal delete-volume button
                                var rowCount = $('#volume_list tr').length;
                                if (rowCount <= 2) {
                                    $('#volume_placeholder').remove().fadeOut();
                                }

                                // Append new row to volume-list
                                $('#volume_list').append(newRow).fadeIn();

                                // Append new option to delete-volume select menu
                                var deleteSelect = 'div#volume-delete-dialog-form > form > fieldset > select#volume';
                                var newOption = '<option value ="' + data.volume_id + '">' + data.volume_name + '</option>';
                                $(deleteSelect).append(newOption);
                            }

                            setVisible('#vol_progressbar', false);
                            setVisible('#create-volume', true);
                            setVisible('#delete-volume', true);
                            disableLinks(false);
                        })
                        .error(function () {

                            message.showMessage('error', 'Server Fault');	// Flag server fault message

                            setVisible('#vol_progressbar', false);
                            setVisible('#create-volume', true);
                            setVisible('#delete-volume', true);
                            disableLinks(false);
                        });

                    $(this).dialog("close");

                    allFields.val("").removeClass("ui-state-error");
                    $('.error').fadeOut().remove();
                }
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
            allFields.val("").removeClass("ui-state-error");
            $('.error').fadeOut().remove();
        }
    })

    // Open modal form when create-volume button is clicked
    $("#create-volume").click(function () {
        $("#volume-dialog-form").dialog("open");
    });
});
