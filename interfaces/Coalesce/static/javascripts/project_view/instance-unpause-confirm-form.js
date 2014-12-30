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
        instance,
        targetRow;

    // Widget Elements
    var progressbar = $("#instance_progressbar");

    $("#instance-unpause-confirm-form").dialog({
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

                // Confirmed Selections
                var confId = id,
                    confInstance = $(instance).text();

                message.showMessage('notice', "Unpausing " + confInstance + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and instance actions
                disableLinks(true);
                disableActions("unpause-instance", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/unpause_server/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Restore actions cell html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            var statusCell = document.getElementById(confId + "-status-cell");

                            // Update status cell
                            $(statusCell).fadeOut().empty();
                            $(statusCell).append("ACTIVE").fadeIn();

                            // Create new actions
                            var newActions =
                                '<a href="/vnc_auto.html?token=' + confId + '" target="_blank">console</a>' +
                                '<span class="instance-actions-pipe"> | </span>' +
                                '<a href="#" class="pause-instance ' + confId + '-disable-action">pause</a>' +
                                '<span class="instance-actions-pipe"> | </span>' +
                                '<a href="#" class="suspend-instance ' + confId + '-disable-action">suspend</a>' +
                                '<span class="instance-actions-pipe"> | </span>' +
                                '<a href="#" class="delete-instance ' + confId + '-disable-action">delete</a>';

                            // Update actions-cell
                            $(actionsCell).fadeOut().empty();
                            $(actionsCell).append(newActions).fadeIn();

                            // Remove paused class
                            $(targetRow).removeClass("instance-paused");
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');

                        // Restore Actions html
                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml).fadeIn();
                    })
                    .always(function () {

                        // Hide progressbar, enabled instance actions and widget view links
                        setVisible(progressbar, false);
                        disableActions("unpause-instance", false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.unpause-instance', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the instance-name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        instance = document.getElementById(id + "-name-text");

        // Add instance-name-text to delete-confirm-form
        $('div#instance-unpause-confirm-form > p > span.instance-name').empty().append($(instance).text());

        $("#instance-unpause-confirm-form").dialog("open");
    });
});
