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
    var name = $("#name"),
        secGroupName = $("#sec_group_name"),
        secKeyName = $("#sec_key_name"),
        networkName = $("#network_name"),
        imageName = $("#image_name"),
        flavorName = $("#flavor_name"),
        allFields = $([]).add(secGroupName).add(secKeyName).add(imageName).add(name).add(networkName),
        error = ".error"; // .error are generated and targeted dynamically

    // Widget Elements
    var progressbar = $("#instance_progressbar"),
        table = $("#instance_list");

    $("#instance-dialog-form").dialog({
        autoOpen: false,
        height: 505,
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
            "Create Instance": function () {

                // Remove UI validation flags
                clearUiValidation(allFields);

                // Validate form inputs
                var isValid =
                    checkLength(name, "Instance Name", 3, 16) &&
                    checkDuplicateName(name, instanceOpts);

                if (isValid) {

                    // Confirmed Selections
                    var confName = name.val(),
                        confSecGroup = secGroupName.val(),
                        confSecKey = secKeyName.val(),
                        confNetwork = networkName.val(),
                        confImage = imageName.val(),
                        confFlavor = flavorName.val();

                    message.showMessage('notice', 'Creating New Instance ' + confName);

                    // Hide widget buttons and disable widget view links
                    setVisible('#create-instance', false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "instances", false);

                    $.getJSON('/create_image/' + confName + '/' + confSecGroup + '/nova/' + confFlavor + '/' + confSecKey + '/' + confImage + '/' + confNetwork + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Generate HTML for new row
                                var newRow =
                                    '<tr id="' + data.server_info.server_id + '"><td id="' + data.server_info.server_id + '-name-cell">' +
                                    '<a href="/' + PROJECT_ID + '/' + data.server_info.server_id + '/instance_view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.server_info.server_id + '-name-text">' + data.server_info.server_name + '</span></a></td>' +
                                    '<td id="' + data.server_info.server_id + '-status-cell">' + data.server_info.server_status + '</td>' +
                                    '<td id="' + data.server_info.server_id + '-os-cell">' + data.server_info.server_os + ' / ' + data.server_info.server_flavor + '</td>' +
                                    '<td id="' + data.server_info.server_id + '-actions-cell">';

                                if (data.server_info.server_status == "ACTIVE") {

                                    newRow +=
                                        '<a href=\"' + data.server_info.novnc_console + '\" class=\"open-instance-console\" onClick=\"window.open(this.href,\'_blank\',\'toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435\'); return false;\">console</a>' +
                                        '<span class="instance-actions-pipe"> | </span>' +
                                        '<a href="#" class="pause-instance ' + data.server_info.server_id + '-disable-action">pause</a><span class="instance-actions-pipe"> | </span>' +
                                        '<a href="#" class="suspend-instance ' + data.server_info.server_id + '-disable-action">suspend</a>';
                                }

                                if (data.server_info.server_status == "PAUSED") {

                                    newRow +=
                                        '<a href="#" class="unpause-instance ' + data.server_info.server_id + '-disable-action">unpause</a>';
                                }

                                if (data.server_info.server_status == "SUSPENDED") {

                                    newRow +=
                                        '<a href="#" class="resume-instance ' + data.server_info.server_id + '-disable-action">resume</a>';
                                }

                                newRow +=
                                    '<span class="instance-actions-pipe"> | </span><a href="#" class="delete-instance ' + data.server_info.server_id + '-disable-action">delete</a></td></tr>';

                                // Check table length, remove placeholder if necessary
                                var rowCount = $('#instance_list tr').length;
                                if (rowCount >= 2) {
                                    $('#instance_placeholder').remove().fadeOut();
                                }

                                // Append new row to instance-list
                                $(table).append(newRow).fadeIn();

                                // Add to instances
                                instances.setItem(
                                    data.server_info.server_id,
                                    { id: data.server_info.server_id, name: data.server_info.server_name, status: data.server_info.server_status,
                                        flavor: data.server_info.server_flavor, os: data.server_info.server_os, console: data.server_info.novnc_console }
                                );
                                instanceOpts.setItem(
                                    data.server_info.server_id,
                                    { value: data.server_info.server_id, option: data.server_info.server_name }
                                );
                                consoleLinks.setItem(
                                    data.server_info.server_id,
                                    {
                                        link: data.server_info.novnc_console,
                                        html: '<a href=\"' + data.server_info.novnc_console + '\" class=\"open-instance-console\" onClick=\"window.open(this.href,\'_blank\',\'toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435\'); return false;\">console</a>'
                                    }
                                );

                                // Update selects
                                addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance"), attachableInstances);
                                addToSelect(data.server_info.server_id, data.server_info.server_name, $("#assign_instance"), assignableInstances);
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            // Reset interface
                            checkAssignFip();
                            disableProgressbar(progressbar, "instances", true);
                            setVisible('#create-instance', true);
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

    $("#create-instance").click(function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        $("#instance-dialog-form").dialog("open");
    });
});