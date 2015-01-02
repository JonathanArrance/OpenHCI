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

    $("#instance-suspend-confirm-form").dialog({
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

                message.showMessage('notice', "Suspending " + confInstance + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and instance actions
                disableLinks(true);
                disableActions("suspend-instance", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "instances", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/suspend_server/')
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
                            $(statusCell).append("SUSPENDED").fadeIn();

                            // Create new actions
                            var newActions =
                                '<a href="#" class="resume-instance ' + confId + '-disable-action">resume</a>' +
                                '<span class="instance-actions-pipe"> | </span>' +
                                '<a href="#" class="delete-instance ' + confId + '-disable-action">delete</a>';

                            // Update actions-cell
                            $(actionsCell).fadeOut().empty();
                            $(actionsCell).append(newActions).fadeIn();

                            // Add paused class
                            $(targetRow).addClass("instance-suspended");

                            // Update instance
                            instances.items[confId].status = "SUSPENDED";
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
                        disableProgressbar(progressbar, "instances", true);
                        disableActions("suspend-instance", false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {

        }
    });

    $(document).on('click', '.suspend-instance', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the instance-name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        instance = document.getElementById(id + "-name-text");

        // Add instance-name-text to confirm-form
        $('div#instance-suspend-confirm-form > p > span.instance-name').empty().append($(instance).text());

        $("#instance-suspend-confirm-form").dialog("open");
    });
});
