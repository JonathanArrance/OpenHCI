$(function () {

    // Widget Elements
    var progressbar = $("#keypair_progressbar"),
        table = $("#keypair_list"),
        placeholder =
            '<tr id="#keypair_placeholder"><td><p><i>You have no keys defined</i></p></td><td></td><td></td></tr>';

    // --- Create ---

    $(function () {

        // Form Elements
        var key_name = $("#key_name"),
            allFields = $([]).add(key_name);

        $("#create-keypair").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#keypair-dialog-form").dialog("open");
        });

        $("#keypair-dialog-form").dialog({
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
                "Create Key Pair": function () {

                    // Remove UI validation flags
                    clearUiValidation(allFields);

                    var isValid =
                        checkLength(key_name, "Key name", standardStringMin, standardStringMax) &&
                        checkCharfield(key_name, "Key name");

                    if (isValid) {

                        // Confirmed Selections
                        var confKeypair = key_name.val();

                        message.showMessage('notice', 'Creating new Key ' + confKeypair);

                        setVisible("#create-keypair", false);
                        disableLinks(true);

                        // Initialize progressbar and make it visible if hidden
                        progressbar.progressbar({value: false});
                        disableProgressbar(progressbar, "keys", false);

                        $.getJSON('/create_sec_keys/' + confKeypair + '/' + PROJECT_ID + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    message.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    message.showMessage('success', data.message);

                                    // Initialize empty string for new router row
                                    var newRow = '';
                                    newRow +=
                                        '<tr id="' + data.key_id + '">' +
                                        '<td id="' + data.key_id + '-name-cell">' +
                                        '<a href="/key_pair/' + data.key_id + '/' + PROJECT_ID + '/view/" class="disable-link" style="color:#696969;">' +
                                        '<span id="' + data.key_id + '-name-text">' + data.key_name + '</span></a></td>' +
                                        '<td id="' + data.key_id + '-user-cell">' +
                                        '<span id="' + data.key_id + '-user-text">' + USERNAME + '</span></td>' +
                                        '<td id="' + data.key_id + '-actions-cell">' +
                                        '<a href="#" class="delete-keypair">delete</a></td></tr>';

                                    // Check to see if this is the first router to be generated, if so remove placeholder and reveal delete-router button
                                    var rowCount = $("#keypair_list tr").length;
                                    if (rowCount <= 2) {
                                        $("#keypair_placeholder").remove().fadeOut();
                                    }

                                    // Append new row to router-list
                                    table.append(newRow).fadeIn();

                                    // Update Selects
                                    addToSelect(data.key_name, data.key_name, $("#sec_key_name"), secKeyInstOpts);
                                    refreshSelect($("#bam-security-select-key"), secKeyInstOpts);
                                    $("#bam-security-select-key").append($('<option></option>')
                                        .val("create")
                                        .html("Create Key"));
                                }
                            })
                            .fail(function () {

                                message.showMessage('error', 'Server Fault');
                            })
                            .always(function () {

                                disableProgressbar(progressbar, "keys", true);
                                setVisible('#create-keypair', true);
                                disableLinks(false);
                                resetUiValidation(allFields);
                            });

                        $(this).dialog("close");
                    }
                }
            },
            close: function () {

                resetUiValidation(allFields);
            }
        });
    });

    // --- Delete ---

    $(function () {

        // Local Variables
        var id = '';
        var keypair = '';
        var targetRow;

        $(document).on('click', '.delete-keypair', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            keypair = document.getElementById(id + "-name-text");

            $('div#keypair-delete-confirm-form > p > span.keypair-name').empty().append($(keypair).text());

            $('#keypair-delete-confirm-form').dialog("open");
        });

        $('#keypair-delete-confirm-form').dialog({
            autoOpen: false,
            height: 125,
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
                "Confirm": function () {

                    // Confirmed Selections
                    var confId = id,
                        confKeypair = $(keypair).text();

                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    message.showMessage('notice', "Deleting " + confKeypair + ".");

                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    progressbar.progressbar({value: false});
                    disableProgressbar(progressbar, "keys", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/key_pair/' + confKeypair + '/' + PROJECT_ID + '/delete/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                                console.log(data);

                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                $(targetRow).fadeOut().remove();

                                // Update selects
                                removeFromSelect(confKeypair, $("#sec_key_name"), secKeyInstOpts);
                                refreshSelect($("#bam-security-select-key"), secKeyInstOpts);
                                $("#bam-security-select-key").append($('<option></option>')
                                    .val("create")
                                    .html("Create Key"));
                            }

                            // If last keypair, reveal placeholder
                            var rowCount = $('#keypair_list tr').length;
                            if (rowCount < 2) {
                                $('#keypair_list').append(placeholder).fadeIn();
                            }

                        })
                        .fail(function () {
                            message.showMessage('error', 'Server Fault');

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            disableLinks(false);
                            disableProgressbar(progressbar, "keys", true);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });
});