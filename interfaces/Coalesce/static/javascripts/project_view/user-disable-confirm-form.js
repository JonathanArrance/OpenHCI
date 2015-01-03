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
        user,
        targetRow;

    // Widget Elements
    var progressbar = $("#users_progressbar");

    $("#user-disable-confirm-form").dialog({
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
                var confRow = targetRow,
                    confId = id,
                    confUsername = $(user).text();

                message.showMessage('notice', "Disabling " + confUsername + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and widgets actions
                disableLinks(true);
                disableActions("disable-user", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "users", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/toggle_user/' + confUsername + '/disable/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Recall clicked action link on error
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Update status and actions cells
                            var newActions =
                                '<a href="#" class="enable-user">enable</a>' +
                                '<span class="user-actions-pipe"> | </span>' +
                                '<a href="#" class="remove-user">remove</a>' +
                                '<span class="user-actions-pipe"> | </span>' +
                                '<a href="#" class="delete-user"> delete</a>';

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(newActions).fadeIn();

                            confRow.addClass("user-disabled");
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
                        disableProgressbar(progressbar, "users", true);
                        disableActions("disable-user", false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            },
            close: function () {
            }
        }
    });

    $(document).on('click', '.disable-user', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        user = document.getElementById(id + "-name-text");

        // Add name-text to form
        $('div#user-disable-confirm-form > p > span.user-name').empty().append($(user).text());
        $("#user-disable-confirm-form").dialog("open");
    });
});
