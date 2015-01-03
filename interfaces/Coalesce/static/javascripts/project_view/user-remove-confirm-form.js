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
    var progressbar = $("#users_progressbar"),
        table = $("#users_list"),
        placeholder = '<tr id="users_placeholder"><td><p><i>This project has no images</i></p></td><td></td></tr>';

    $('#user-remove-confirm-form').dialog({
        autoOpen: false,
        height: 125,
        width: 200,
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

                message.showMessage('notice', "Removing " + confUsername + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and widgets actions
                disableLinks(true);
                disableActions("remove-user", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "users", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/remove_user_from_project/' + confId + '/' + PROJECT_ID + '/')
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

                            // Update users
                            users.items[confUsername].removed = "TRUE";

                            // Update select
                            addToSelect(confUsername, confUsername, $("select#username"), orphanedUserOpts);

                            // If last user, reveal placeholder
                            var rowCount = $('#users_list tr').length;
                            if (rowCount < 2) {
                                table.append(placeholder).fadeIn();
                            }
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
                        disableActions("remove-user", false);
                        disableLinks(false);
                        checkAddUser();
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.remove-user', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        user = document.getElementById(id + "-name-text");

        // Add name-text to form
        $('div#user-remove-confirm-form > p > span.user-name').empty().append($(user).text());
        $('#user-remove-confirm-form').dialog("open");
    });
});




