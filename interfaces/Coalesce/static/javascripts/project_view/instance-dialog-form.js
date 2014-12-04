$(function () {

    var csrftoken = getCookie('csrftoken');
    var sec_group_name = $("#sec_group_name"),
        sec_key_name = $("#sec_key_name"),
        image_name = $("#image_name"),
        name = $("#name"),
        network_name = $("#network_name"),
        flavor_name = $("#flavor_name"),
        allFields = $([]).add(sec_group_name).add(sec_key_name).add(image_name).add(name).add(network_name),
        tips = $(".validateTips");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#instance-dialog-form").dialog({
        autoOpen: false,
        height: 600,
        width: 350,
        modal: true,
        buttons: {
            "Create an instance": function () {

                var bValid = true;
                allFields.removeClass("ui-state-error"); 	// Remove UI validation flags
                $('.error').fadeOut().remove();
                bValid = bValid && checkLength(tips, name, "Instance Name", 3, 16);	// Validate image_name length

                if (bValid) {

                    message.showMessage('notice', 'Creating New Instance ' + name.val());

                    setVisible('#create-instance', false);
                    setVisible('#delete-instance', false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $('#instance_progressbar').progressbar({value: false});
                    setVisible('#instance_progressbar', true);

                    $.getJSON('/create_image/' + name.val() + '/' + sec_group_name.val() + '/nova/' + flavor_name.val() + '/' + sec_key_name.val() + '/' + image_name.val() + '/' + network_name.val() + '/' + PROJECT_ID + '/')
                        .success(function (data) {

                            if (data.status == 'error') {
                                message.showMessage('error', data.message);
                            }
                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var newRow = '';    // Initialize empty string for new instance row

                                // --- BEGIN html string generation
                                // Start row
                                newRow += '<tr id="' + data.server_info.server_id + '">';
                                // Create name-cell
                                newRow += '<td id="' + data.server_info.server_id + '-name-cell">';
                                newRow += '<a href="/' + PROJECT_ID + '/' + data.server_info.server_id + '/instance_view/" class="disable-link" onclick="false" style="color:#696969;">';
                                newRow += '<span id="' + data.server_info.server_id + '-name-text">' + data.server_info.server_name + '</span></a></td>';
                                // Create status-cell
                                newRow += '<td id="' + data.server_info.server_id + '-status-cell">' + data.server_info.server_status + '</td>';
                                // Create os-cell
                                newRow += '<td id="' + data.server_info.server_id + '-os-cell">' + data.server_info.server_os + ' / ' + data.server_info.server_flavor + '</td>';
                                // Start actions-cell
                                newRow += '<td id="' + data.server_info.server_id + '-actions-cell">';
                                // Populate actions-cell
                                if (data.server_info.server_status == "ACTIVE") {
                                    newRow += '<a href="' + data.server_info.novnc_console + '" target="_blank">console</a>';
                                    newRow += '<span class="instance-actions-pipe"> | </span>';
                                    newRow += '<a href="#" class="pause-instance '+data.server_info.server_id+'-disable-action">pause</a>';
                                    newRow += '<span class="instance-actions-pipe"> | </span>';
                                    newRow += '<a href="#" class="suspend-instance '+data.server_info.server_id+'-disable-action">suspend</a>';
                                }
                                if (data.server_info.server_status == "PAUSED") {
                                    newRow += '<a href="#" class="unpause-instance '+data.server_info.server_id+'-disable-action">unpause</a>';
                                }
                                if (data.server_info.server_status == "SUSPENDED") {
                                    newRow += '<a href="#" class="resume-instance '+data.server_info.server_id+'-disable-action">resume</a>';
                                }
                                // End actions-cell and row
                                newRow += '</td></tr>';
                                // --- END html string generation

                                // If first instance, remove placeholder
                                var rowCount = $('#instance_list tr').length;
                                if (rowCount <= 2) {
                                    $('#instance_placeholder').remove().fadeOut();
                                }

                                // Append new row to instance-list
                                $('#instance_list').append(newRow).fadeIn();

                                // Create a new option for the new instance
                                var newOption = '<option value=' + data.server_info.server_id + '>' + data.server_info.server_name + '</option>';

                                // Append new option to delete-instance select menu
                                var deleteSelect = 'div#instance-delete-dialog-form > form > fieldset > select#instance';
                                $(deleteSelect).append(newOption);

                                // Append new option to attach-volume select menu
                                var attachSelect = 'div#volume-attach-dialog-form > form  > fieldset > select#instance';
                                $(attachSelect).append(newOption);

                                // Append new option to assign-fip select menu
                                var assignSelect = 'div#fip-assign-dialog-form > form > fieldset > select#assign_instance';
                                $(assignSelect).append(newOption);
                            }

                            setVisible('#instance_progressbar', false);
                            setVisible('#delete-instance', true);
                            setVisible('#create-instance', true);
                            disableLinks(false);
                        })
                        .error(function () {

                            message.showMessage('error', 'Server Fault');

                            setVisible('#instance_progressbar', false);
                            setVisible('#delete-instance', true);
                            setVisible('#create-instance', true);
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
    });

    $("#create-instance").click(function () {
        $("#instance-dialog-form").dialog("open");
    });
});