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

    // Dialog Elements
    var ports = $("#ports"),
        groupName = $("#groupname"),
        groupDesc = $("#groupdesc"),
        allFields = $([]).add(ports).add(groupName).add(groupDesc);

    // Widget Elements
    var progressbar = $("#secGroup_progressbar"),
        createButton = $("#create-security-group"),
        table = $("#secGroup_list");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#sec-group-dialog-form").dialog({
        autoOpen: false,
        height: 385,
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
            "Create a security group": function () {

                // Remove UI validation flags
                clearUiValidation(allFields);

                var isValid =
                    checkLength(groupName, "Group Name", 3, 16) &&
                    checkLength(groupDesc, "Group Description", 6, 80);

                if (isValid) {

                    var confPorts = ports.val(),
                        confName = groupName.val(),
                        confDesc = groupDesc.val();

                    if (confPorts == "") {
                        confPorts = "443,80,22";
                    }

                    message.showMessage('notice', 'Creating new Key ' + confName);

                    setVisible("#create-security-group", false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    setVisible(progressbar, true);

                    $.getJSON('/create_security_group/' + confName + '/' + confDesc + '/' + confPorts + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new router row
                                var newRow = '';
                                newRow +=
                                    '<tr id="' + data.sec_group_id + '"><td id="' + data.sec_group_id + '-name-cell">' +
                                    '<span id="' + data.sec_group_id + '-name-text">' + data.sec_group_name + '</span></td>' +
                                    '<td id="' + data.sec_group_id + '-username-cell">' +
                                    '<span id="' + data.sec_group_id + '-username-text">' + data.username + '</span></td>' +
                                    '<td id="' + data.sec_group_id + '-actions-cell"><a href="#" class="delete-secGroup">delete</a>' +
                                    '</td></tr>';

                                // Check to see if this is the first sec group to be generated
                                var rowCount = $("#secGroup_list tr").length;
                                if (rowCount <= 2) {
                                    $("#secGroup_placeholder").remove().fadeOut();
                                }

                                // Append new row to router-list
                                table.append(newRow).fadeIn();

                                // Update selects
                                addToSelect(data.sec_group_name, data.sec_group_name, $("#sec_group_name"), secGroupInstOpts);
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            setVisible(progressbar, false);
                            setVisible('#create-security-group', true);
                            disableLinks(false);
                            resetUiValidation(allFields);
                            ports.val("443,80,22");
                        });

                    $(this).dialog("close");
                }
            }
        },
        close: function () {

            resetUiValidation(allFields);
        }
    });

    $("#create-security-group")
        .click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#sec-group-dialog-form").dialog("open");
        });
});
