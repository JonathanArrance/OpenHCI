$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Elements
    var ports = $("#ports"),
        groupName = $("#groupname"),
        groupDesc = $("#groupdesc"),
        allFields = $([]).add(ports).add(groupName).add(groupDesc),
        tips = $(".validateTips");

    // Widget Elements
    var progressbar = $("#secGroup_progressbar"),
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
        height: 400,
        width: 350,
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

                allFields.removeClass("ui-state-error");
                $('.error').fadeOut().remove();

                var bValid = true;
                bValid =
                    bValid &&
                    checkLength(tips, groupName, "groupname", 3, 16) &&
                    checkLength(tips, groupDesc, "groupdesc", 6, 80);

                if (bValid) {

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
                        });

                    $(this).dialog("close");

                    allFields.val("").removeClass("ui-state-error");
                    ports.val("443,80,22");
                    $('.error').fadeOut().remove();
                }
            }
        },
        close: function () {

            allFields.val("").removeClass("ui-state-error");
            $('.error').fadeOut().remove();
        }
    });

    $("#create-security-group")
        .click(function () {
            $("#sec-group-dialog-form").dialog("open");
        });
});
