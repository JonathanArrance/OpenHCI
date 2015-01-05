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
        router,
        targetRow;

    // Widget Elements
    var progressbar = $("#router_progressbar"),
        table = $("#router_list"),
        placeholder = '<tr id="router_placeholder"><td><p><i>This project has no routers</i></p></td><td></td><td></td></tr>';

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

                message.showMessage('notice', "Deleting " + confRouter + ".");

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

                            message.showMessage('error', data.message);

                            // Restore actions cell html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

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

                        message.showMessage('error', 'Server Fault');

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
});




