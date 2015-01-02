$(function () {

    var csrftoken = getCookie('csrftoken');
    var username = '';
    var userId = '';
    var row = '';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#user-enable-confirm-form").dialog({
        autoOpen: false,
        height: 150,
        width: 250,
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

                message.showMessage('notice', 'Disabling user');

                var confirmedUsername = $(username).text();
                var confirmedId = userId;
                var confirmedRow = row;
                var actionsCell = document.getElementById(confirmedId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Create loader
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                disableActions("enable-user", true);
                disableLinks(true);

                $.getJSON('/toggle_user/' + confirmedUsername + '/enable/')
                    .success(function (data) {

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
                                '<a href="#" class="disable-user">disable</a>' +
                                '<span class="user-actions-pipe"> | </span>' +
                                '<a href="#" class="remove-user">remove</a>' +
                                '<span class="user-actions-pipe"> | </span>' +
                                '<a href="#" class="delete-user"> delete</a>';

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(newActions).fadeIn();

                            confirmedRow.removeClass("user_disabled");
                        }

                        disableActions("enable-user", false);
                        disableLinks(false);
                    })
                    .error(function () {

                        message.showMessage('error', 'Server Fault');

                        // Recall clicked action link on server fault
                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml).fadeIn();

                        disableActions("enable-user", false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            },
            close: function () {
            }
        }
    });

    $(document).on('click', '.enable-user', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        userId = $(this).parent().parent().attr('id');
        row = $(this).parent().parent();

        // Clear and add username to .username span in confirm statement
        username = '#' + userId + '-name-text';
        $('#user-enable-confirm-form > p > span.user-name').empty().append($(username).text());

        $("#user-enable-confirm-form").dialog("open");
    });
});
