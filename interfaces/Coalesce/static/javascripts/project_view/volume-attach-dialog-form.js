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

    // Widget Elements
    var progressbar = $("#vol_progressbar");

    $("#volume-attach-dialog-form").dialog({
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
            "Attach Volume": function () {

                // Form elements
                var instance = $("#instance");

                // Confirmed Selections
                var confRow = targetRow,
                    confId = id,
                    confVol = $(volume).text(),
                    confInstance = instanceOpts.items[instance.val()].value,
                    confInstanceName = instanceOpts.items[confInstance].option;

                message.showMessage('notice', 'Attaching ' + confVol + ' to ' + confInstanceName + '.');

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and instance actions
                disableLinks(true);
                disableActions("attach-volume", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "volumes", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/attach_volume/' + PROJECT_ID + '/' + confInstance + '/' + confId + '/')
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
                                '<a href="#" class="detach-volume">detach</a>';

                            $(actionsCell).append(newActions).fadeIn();
                            $(targetAttached).append(confInstanceName).fadeIn();

                            confRow.addClass("volume-attached");
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
                        disableActions("attach-volume", false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.attach-volume', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        volume = document.getElementById(id + "-name-text");

        // Add name-text to form
        $('div#volume-attach-dialog-form > p > span.volume-name').empty().append($(volume).text());

        $('#volume-attach-dialog-form').dialog("open");
    });
});
