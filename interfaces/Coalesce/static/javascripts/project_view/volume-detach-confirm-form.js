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
        volume,
        targetRow;

    // Form elements
    var instance = $("#instance");

    // Widget Elements
    var progressbar = $("#vol_progressbar");

    $("#volume-detach-confirm-form").dialog({
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
            "Detach Volume": function () {

                // Confirmed Selections
                var confRow = targetRow,
                    confId = id,
                    confVol = $(volume).text(),
                    confInstance = instance.val(),
                    confInstanceName = instanceOpts.items[confInstance].option;

                message.showMessage('notice', 'Detaching ' + confVol + ' from ' + confInstanceName + '.');

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and instance actions
                disableLinks(true);
                disableActions("detach-volume", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "volumes", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/detach_volume/' + PROJECT_ID + '/' + confId + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Restore actions cell html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Update row
                            var targetAttached = document.getElementById(confId + "-attached-cell");

                            $(actionsCell).empty().fadeOut();
                            $(targetAttached).empty().fadeOut();

                            var newActions =
                                '<a href="#" class="attach-volume">attach</a>' +
                                '<span class="volume-actions-pipe"> | </span>' +
                                '<a href="#" class="delete-volume">delete</a>';

                            $(actionsCell).append(newActions).fadeIn();
                            $(targetAttached).append("No Attached Instance").fadeIn();

                            confRow.removeClass("volume-attached");
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
                        disableProgressbar(progressbar, "volumes", true);
                        disableLinks(false);
                        disableActions("detach-volume", false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.detach-volume', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        targetRow = $(this).parent().parent();
        id = targetRow.attr("id");
        volume = document.getElementById(id + "-name-text");

        // Add name-text to form
        $('div#volume-detach-confirm-form > p > span.volume-name').empty().append($(volume).text());

        $('#volume-detach-confirm-form').dialog("open");
    });
});