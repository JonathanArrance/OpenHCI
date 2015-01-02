$(function () {

    var csrftoken = getCookie('csrftoken');
    var id = '';
    var user = '';
    var targetRow;

    // Widget Elements
    var progressbar = $("#users_progressbar"),
        placeholder = '<tr id="#users_placeholder"><td><p><i>This project has no images</i></p></td><td></td></tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#user-delete-confirm-form').dialog({
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
                var confId = id,
                    confUsername = $(user).text();

                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                message.showMessage('notice', "Deleting " + confUsername + ".");

                disableLinks(true);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/delete_user/' + confUsername + '/' + confId + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();
                        }

                        // If last user, reveal placeholder
                        var rowCount = $('#users_list tr').length;
                        if (rowCount < 2) {
                            $('#users_list').append(placeholder).fadeIn();
                        }

                    })
                    .fail(function () {
                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml).fadeIn();
                    })
                    .always(function () {
                        disableLinks(false);
                        setVisible(progressbar, false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
            $(this).dialog("close");
        }
    });

    $(document).on('click', '.delete-user', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        user = document.getElementById(id + "-name-text");

        $('div#user-delete-confirm-form > p > span.user-name').empty().append($(user).text());

        $('#user-delete-confirm-form').dialog("open");
    });
});




