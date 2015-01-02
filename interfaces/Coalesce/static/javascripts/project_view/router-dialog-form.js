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
    var router_name = $("#router_name"),
        priv_net = $("#priv_net"),
        allFields = $([]).add(router_name).add(priv_net);

    // Widget Elements
    var progressbar = $("#router_progressbar"),
        createButton = $("#create-router"),
        placeholder = $("#router_placeholder"),
        table = $('#router_list');

    $("#router-dialog-form").dialog({
        autoOpen: false,
        height: 285,
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
            "Create Router": function () {

                // Remove UI validation flags
                clearUiValidation(allFields);

                var isValid =
                    checkLength(router_name, "Router Name", 3, 16) &&
                    checkDuplicateName(router_name, routers);

                if (isValid) {

                    // Confirmed Selections
                    var confRouter = router_name.val(),
                        confPrivateNet = priv_net.val();

                    message.showMessage('notice', 'Creating new router ' + confRouter);

                    // Disable widget view links and hide create button
                    disableLinks(true);
                    setVisible(createButton, false);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "routers", false);

                    $.getJSON('/create_router/' + confRouter + '/' + confPrivateNet + '/' + DEFAULT_PUBLIC + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new router row
                                var newRow =
                                    '<tr id="' + data.router_id + '">' +
                                    '<td id="' + data.router_id + '-name-cell">' +
                                    '<a href="/router/' + data.router_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.router_id + '-name-text">' + data.router_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.router_id + '-status-cell"><span id="' + data.router_id + '-status-text">ACTIVE</span></td>' +
                                    '<td id="' + data.router_id + '-actions-cell"><a href="#" class="delete-router">delete</a></td>' + '</tr>';

                                // Check to see if this is the first router to be generated, if so remove placeholder and reveal delete-router button
                                var rowCount = $("#router_list tr").length;
                                if (rowCount <= 2) {
                                    placeholder.remove().fadeOut();
                                }

                                // Append new row to router-list
                                table.append(newRow).fadeIn();

                                // Add to routers
                                routers.setItem(data.router_id, { name: data.router_name, network: confPrivateNet });

                                // Update selects
                                removeFromSelect(confPrivateNet, $("#priv_net"), privNetRoutOpts);

                                // Update private network
                                privateNetworks.items[confPrivateNet].router = data.router_id;
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            // Reset interface
                            disableProgressbar(progressbar, "routers", true);
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

    $("#create-router")
        .click(function () {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#router-dialog-form").dialog("open");
        });
});
