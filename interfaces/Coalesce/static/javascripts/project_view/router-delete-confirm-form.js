$(function () {

    var csrftoken = getCookie('csrftoken');
    var id = '';
    var router = '';
    var targetRow;

    // Widget Elements
    var placeholder = '<tr id="router_placeholder"><td><p><i>This project has no routers</i></p></td><td></td><td></td></tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#router-delete-confirm-form').dialog({
        autoOpen: false,
        height: 125,
        width: 150,
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

                var confirmedId = id;
                var deleteHtml = '<a href="#" class="delete-router">delete</a></td>';

                message.showMessage('notice', "Deleting " + $(router).text() + ".");

                setVisible('#create-router', false);
                disableLinks(true);

                // Create loader
                var actionsCell = document.getElementById(confirmedId + "-actions-cell");
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/delete_router/' + PROJECT_ID + '/' + confirmedId + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(deleteHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();
                        }

                        // If last router, reveal placeholder
                        var rowCount = $('#router_list tr').length;
                        if (rowCount < 2) {
                            $('#router_list').append(placeholder).fadeIn();
                        }

                    })
                    .fail(function () {
                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(deleteHtml).fadeIn();
                    })
                    .always(function () {
                        setVisible('#create-router', true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
            $(this).dialog("close");
        }
    });

    $(document).on('click', '.delete-router', function () {

        event.preventDefault();

        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        router = document.getElementById(id + "-name-text");

        $('div#router-delete-confirm-form > p > span.router-name').empty().append($(router).text());

        $('#router-delete-confirm-form').dialog("open");
    });
});




