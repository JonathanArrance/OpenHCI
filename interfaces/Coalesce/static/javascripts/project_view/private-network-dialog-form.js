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

    // Dialog Form Elements
    var privateNet = $("#privateNet_name"),
        admin_state = $("#admin_state"),
        shared = $("#shared"),
        allFields = $([]).add(privateNet).add(admin_state).add(shared);

    // Widget Elements
    var progressbar = $("#privateNet_progressbar"),
        createButton = $("#create-private-network"),
        placeholder = $("#privateNet_placeholder"),
        table = $("#privateNet_list");

    $("#private-network-dialog-form").dialog({
        autoOpen: false,
        height: 350,
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
            "Create Private Network": function () {

                // Remove UI validation flags
                clearUiValidation(allFields);

                var isValid =
                    checkLength(privateNet, "Network Name", 3, 16) &&
                    checkDuplicateName(privateNet, privateNetworks);

                if (isValid) {

                    // Confirmed Selections
                    var confPrivateNet = privateNet.val(),
                        confShared = shared.val(),
                        confAdminState = admin_state.val();

                    message.showMessage('notice', 'Creating new router ' + confPrivateNet);

                    // Disable widget view links and hide create button
                    disableLinks(true);
                    setVisible(createButton, false);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "privateNets", false);

                    $.getJSON('/add_private_network/' + confPrivateNet + '/' + confAdminState + '/' + confShared + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new network row
                                var newRow =
                                    '<tr id="' + data.net_id + '">' +
                                    '<td id="' + data.net_id + '-name-cell">' +
                                    '<a href="/network/' + data.net_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.net_id + '-name-text">' + data.net_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.net_id + '-status-cell">' +
                                    'shared: <span id="' + data.net_id + '-shared-text">' + confShared + '</span>' +
                                    '<span id="{{ value.net_id }}-status-pipe"> | </span>' +
                                    'admin state: <span id="' + data.net_id + '-admin-text">' + confAdminState + '</span></td>' +
                                    '<td id="' + data.net_id + '-subnet-cell"><span id="' + data.subnet.subnet_id + '">' + data.subnet.subnet_name + '</span></td>' +
                                    '<td id="' + data.net_id + '-actions-cell"><a href="#" class="delete-privateNet">delete</a></td>' + '</tr>';

                                // Check to see if this is the first network to be generated, if so remove placeholder
                                var rowCount = $("#privateNet_list tr").length;
                                if (rowCount > 2) {
                                    placeholder.remove().fadeOut();
                                    setVisible('#create-router', true)
                                }

                                // Append new row
                                table.append(newRow).fadeIn();

                                // Add to privateNetworks
                                privateNetworks.setItem(data.net_id, { id: data.net_id, name: data.net_name, router: "None" });

                                // Update selects
                                addToSelect(data.net_name, data.net_name, $("#network_name"), privNetInstOpts);
                                addToSelect(data.net_id, data.net_name, $("#priv_net"), privNetRoutOpts);
                            }

                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');	// Flag server fault message
                        })
                        .always(function () {

                            // Reset interface
                            disableProgressbar(progressbar, "privateNets", true);
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

    $("#create-private-network")
        .click(function () {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#private-network-dialog-form").dialog("open");
        });

    // If placeholder exists, hide create-router
    $(document).ready(function () {
        if ($('#privateNet_placeholder').length) {
            setVisible('#create-router', false)
        }
    });
});
