$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Form Elements
    var key_name = $("#key_name"),
        allFields = $([]).add(key_name),
        tips = $(".validateTips");

    // Widget Elements
    var progressbar = $("#keypair_progressbar"),
        table = $("#keypair_list");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
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
                    checkLength(key_name, "key name", 3, 16);

                if (isValid) {

                    // Confirmed Selections
                    var confKeypair = key_name.val();

                    message.showMessage('notice', 'Creating new Key ' + confKeypair);

                    setVisible("#create-keypair", false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    setVisible(progressbar, true);

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
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            setVisible(progressbar, false);
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

    $("#create-keypair")
        .click(function () {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#keypair-dialog-form").dialog("open");
        });
});
