$(function () {

    // Widget Elements
    var progressbar = $("#router_progressbar"),
        table = $('#router_list'),
        placeholder = '<tr id="router_placeholder"><td><p><i>This project has no routers</i></p></td><td></td><td></td></tr>';

    // --- Create ---

    $(function () {

        // Form Elements
        var router_name = $("#router_name"),
            priv_net = $("#priv_net"),
            allFields = $([]).add(router_name).add(priv_net);

        $("#create-router").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#router-dialog-form").dialog("open");
        });

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
                        checkLength(router_name, "Router name", standardStringMin, standardStringMax) &&
                        checkCharfield(router_name, "Router name") &&
                        checkDuplicateName(router_name, routers);

                    if (isValid) {

                        // Confirmed Selections
                        var confRouter = router_name.val(),
                            confPrivateNet = priv_net.val();

                        messages.showMessage('notice', 'Creating new router ' + confRouter);

                        // Disable widget view links and hide create button
                        disableLinks(true);
                        setVisible("#create-router", false);

                        // Initialize progressbar and make it visible if hidden
                        $(progressbar).progressbar({value: false});
                        disableProgressbar(progressbar, "routers", false);

                        $.getJSON('/create_router/' + confRouter + '/' + confPrivateNet + '/' + DEFAULT_PUBLIC + '/' + PROJECT_ID + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    messages.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    messages.showMessage('success', data.message);

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
                                        $("#router_placeholder").remove().fadeOut();
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

                                messages.showMessage('error', 'Server Fault');
                            })
                            .always(function () {

                                // Reset interface
                                disableProgressbar(progressbar, "routers", true);
                                setVisible("#create-router", true);
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
    });

    // --- Delete ---

    $(function () {

        // Local Variables
        var id,
            router,
            targetRow;

        $(document).on('click', '.delete-router', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            router = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#router-delete-confirm-form > p > span.router-name').empty().append($(router).text());

            $('#router-delete-confirm-form').dialog("open");
        });

        $('#router-delete-confirm-form').dialog({
            autoOpen: false,
            height: 125,
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
                "Confirm": function () {

                    var confId = id,
                        confRouter = $(router).text(),
                        confRow = targetRow;

                    messages.showMessage('notice', "Deleting " + confRouter + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("delete-router", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "routers", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/delete_router/' + PROJECT_ID + '/' + confId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                messages.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

                                // Remove row
                                confRow.fadeOut().remove();

                                // If last router, reveal placeholder
                                var rowCount = $('#router_list tr').length;
                                if (rowCount < 2) {
                                    $(table).append(placeholder).fadeIn();
                                }

                                if (routers.items[confId].network) {
                                    // Update selects
                                    addToSelect(routers.items[confId].network, privateNetworks.items[routers.items[confId].network].name, $("#priv_net"), privNetRoutOpts);

                                    // Update private network
                                    privateNetworks.items[routers.items[confId].network].router = "None";
                                }

                                // Remover from routers
                                routers.removeItem(confId);
                            }

                        })
                        .fail(function () {

                            messages.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "routers", true);
                            disableLinks(false);
                            disableActions("delete-router", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });
});