$(function () {

    // Widget Elements
    var progressbar = $("#secGroup_progressbar"),
        table = $("#secGroup_list"),
        placeholder =
            '<tr id="#secGroup_placeholder"><td><p><i>You have no keys defined</i></p></td><td></td><td></td></tr>';

    // --- Create ---

    $(function () {

        // Dialog Elements
        var ports = $("#ports"),
            groupName = $("#groupname"),
            groupDesc = $("#groupdesc"),
            allFields = $([]).add(ports).add(groupName).add(groupDesc);

        $("#create-security-group").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#sec-group-dialog-form").dialog("open");
        });

        $("#sec-group-dialog-form").dialog({
            autoOpen: false,
            height: 410,
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

                    if (!isValid) {
                    } else {

                        var confPorts = ports.val(),
                            confTransport = $('input[name=transport]:checked').val(),
                            confName = groupName.val(),
                            confDesc = groupDesc.val();

                        if (confPorts == "") {
                            confPorts = "443,80,22";
                        }

                        if (confTransport == undefined) {
                            confTransport = 'tcp';
                        }

                        message.showMessage('notice', 'Creating new Key ' + confName);

                        setVisible("#create-security-group", false);
                        disableLinks(true);

                        // Initialize progressbar and make it visible if hidden
                        $(progressbar).progressbar({value: false});
                        setVisible(progressbar, true);

                        $.getJSON('/create_security_group/' + confName + '/' + confDesc + '/' + confPorts + '/' + confTransport + '/' + PROJECT_ID + '/')
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
                                        '<a href="/security_group/' + data.sec_group_id + '/' + PROJECT_ID + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                        '<span id="' + data.sec_group_id + '-name-text">' + data.sec_group_name + '</span></td>' +
                                        '<td id="' + data.sec_group_id + '-username-cell">' +
                                        '<span id="' + data.sec_group_id + '-username-text">' + data.username + '</span></td>' +
                                        '<td id="' + data.sec_group_id + '-actions-cell"><a href="#" class="delete-secGroup">delete</a>' +
                                            // '<span> | </span><a href="#" class="update-secGroup">update</a></td>' +
                                        '</tr>';

                                    // Check to see if this is the first sec group to be generated
                                    var rowCount = $("#secGroup_list tr").length;
                                    if (rowCount <= 2) {
                                        $("#secGroup_placeholder").remove().fadeOut();
                                    }

                                    // Append new row to router-list
                                    table.append(newRow).fadeIn();

                                    // Update selects
                                    addToSelect(data.sec_group_name, data.sec_group_name, $("#sec_group_name"), secGroupInstOpts);
                                    refreshSelect($("#bam-security-group"), secGroupInstOpts);
                                }
                            })
                            .fail(function () {

                                message.showMessage('error', 'Server Fault');
                            })
                            .always(function () {

                                setVisible(progressbar, false);
                                setVisible("#create-security-group", true);
                                disableLinks(false);
                                resetUiValidation(allFields);
                                $("input#tcp").prop('checked', true);
                                ports.val("443,80,22");
                            });

                        $(this).dialog("close");
                    }
                }
            },
            close: function () {

                // Reset UI
                resetUiValidation(allFields);
            }
        });
    });

    // --- Delete ---

    $(function () {

        // Local Variables
        var id = '';
        var secGroup = '';
        var targetRow;

        $(document).on('click', '.delete-secGroup', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            secGroup = document.getElementById(id + "-name-text");

            $('div#sec-group-delete-confirm-form > p > span.secGroup-name').empty().append($(secGroup).text());

            $('#sec-group-delete-confirm-form').dialog("open");
        });

        $('#sec-group-delete-confirm-form').dialog({
            autoOpen: false,
            height: 125,
            width: 245,
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
                        confSecGroup = $(secGroup).text();

                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    message.showMessage('notice', "Deleting " + confSecGroup + ".");

                    disableLinks(true);

                    // Disable actions
                    disableActions("delete-secGroup", true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    setVisible(progressbar, true);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/delete_sec_group/' + confId + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                $(targetRow).fadeOut().remove();
                            }

                            // If last security group, reveal placeholder
                            var rowCount = $('#secGroup_list tr').length;
                            if (rowCount < 2) {
                                $('#secGroup_list').append(placeholder).fadeIn();
                            }

                            // Update selects
                            removeFromSelect(confSecGroup, $("#sec_group_name"), secGroupInstOpts);
                            refreshSelect($("#bam-security-group"), secGroupInstOpts);
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            disableLinks(false);
                            disableActions("delete-secGroup", false);
                            setVisible(progressbar, false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });
});