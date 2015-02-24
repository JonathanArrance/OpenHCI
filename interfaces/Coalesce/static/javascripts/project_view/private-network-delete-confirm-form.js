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

    // Local Variables
    var id,
        privateNet,
        targetRow;

    // Widget Elements
    var progressbar = $("#privateNet_progressbar"),
        table = $("#privateNet_list"),
        placeholder = '<tr id="privateNet_placeholder"><td><p><i>This project has no privateNets</i></p></td><td></td><td></td><td></td></tr>';

    $('#private-network-delete-confirm-form').dialog({
        autoOpen: false,
        height: 150,
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

                // Confirmed Selections
                var confId = id,
                    confPrivateNet = $(privateNet).text(),
                    confRow = targetRow;

                message.showMessage('notice', "Deleting " + confPrivateNet + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and instance actions
                disableLinks(true);
                disableActions("delete-privateNet", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "privateNets", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                // Disable Router
                var routerNet = privateNetworks.items[confId],
                    routerId = routerNet.router,
                    routerRow = $(document.getElementById(routerId));

                if (routerId != "None") {

                    // Add class to indicate router is being deleted
                    routerRow.addClass("router-deleted");

                    // Disable router actions
                    disableActions("delete-router", true);

                    // Initialize progressbar and make it visible
                    $("#router_progressbar").progressbar({value: false});
                    disableProgressbar("#router_progressbar", "routers", false);
                }

                // --- Delete Private Network

                $.getJSON('/delete_private_network/' + PROJECT_ID + '/' + confId + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Restore actions cell html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();

                            if (routerId != "None") {

                                        checkCreateRouter();
                                        disableProgressbar("#router_progressbar", "routers", true);
                                        disableActions("delete-router", false);
                                        disableLinks(false);
                                        routerRow.removeClass("router-deleted");
                            }
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Remove row
                            confRow.fadeOut().remove();

                            // If last privateNet, reveal placeholder
                            var rowCount = $('#privateNet_list tr').length;
                            if (rowCount < 2) {
                                $(table).append(placeholder).fadeIn();
                                setVisible($("#create-router"), false);
                            }

                            // --- Delete Router

                            if (routerId != "None") {
                                $.getJSON('/delete_router/' + PROJECT_ID + '/' + routerId + '/')
                                    .done(function (data) {

                                        var confRouterId = routerId;

                                        if (data.status == 'error') {

                                            message.showMessage('error', data.message);
                                        }

                                        if (data.status == 'success') {

                                            message.showMessage('success', data.message);

                                            // Remove row
                                            routerRow.fadeOut().remove();

                                            // If last router, reveal placeholder
                                            var rowCount = $('#router_list tr').length;
                                            if (rowCount < 2) {
                                                $('#router_list').append(
                                                    '<tr id="router_placeholder"><td><p><i>This project has no routers</i></p></td><td></td><td></td></tr>'
                                                ).fadeIn();
                                            }

                                            // Remover from routers
                                            routers.removeItem(confRouterId);
                                        }
                                    })
                                    .fail(function () {

                                        message.showMessage('error', 'Server Fault');

                                        // Add class to indicate router is being deleted
                                        routerRow.removeClass("router-deleted");
                                    })
                                    .always(function () {

                                        checkCreateRouter();
                                        disableProgressbar("#router_progressbar", "routers", true);
                                        disableActions("delete-router", false);
                                        disableLinks(false);
                                    });
                            }
                            // ---

                            // Remove private network
                            privateNetworks.removeItem(confId);

                            // Update selects
                            removeFromSelect(confPrivateNet, $("#network_name"), privNetInstOpts);
                            removeFromSelect(confId, $("#priv_net"), privNetRoutOpts);
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');

                        // Restore Actions html
                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml).fadeIn();
                    })
                    .always(function () {

                        // Hide progressbar and enable widget view links
                        disableProgressbar(progressbar, "privateNets", true);
                        disableActions("delete-privateNet", false);
                        if (routerId == "None") {
                            disableLinks(false);
                        }
                    });
                // ---

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.delete-privateNet', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        privateNet = document.getElementById(id + "-name-text");

        // Add name-text to form
        $('div#private-network-delete-confirm-form > p > span.privateNet-name').empty().append($(privateNet).text());

        $('#private-network-delete-confirm-form').dialog("open");
    });
});




