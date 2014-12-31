$(function () {

    var csrftoken = getCookie('csrftoken');
    var id = '';
    var privateNet = '';
    var targetRow;

    // Widget Elements
    var progressbar = $("#privateNet_progressbar"),
        placeholder = '<tr id="privateNet_placeholder"><td><p><i>This project has no privateNets</i></p></td><td></td><td></td></tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#private-network-delete-confirm-form').dialog({
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

                var confirmedId = id;
                var confPrivateNet = $(privateNet).text();
                var deleteHtml = '<a href="#" class="delete-privateNet">delete</a></td>';

                message.showMessage('notice', "Deleting " + confPrivateNet + ".");

                disableLinks(true);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "privateNets", false);

                // Create loader
                var actionsCell = document.getElementById(confirmedId + "-actions-cell");
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/delete_private_network/' + PROJECT_ID + '/' + confirmedId + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(deleteHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();

                            // Update selects
                            removeFromSelect(confPrivateNet, $("#network_name"), privateNetworks);
                        }

                        // If last privateNet, reveal placeholder
                        var rowCount = $('#privateNet_list tr').length;
                        if (rowCount < 2) {
                            $('#privateNet_list').append(placeholder).fadeIn();
                        }

                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(deleteHtml).fadeIn();
                    })
                    .always(function () {

                        disableProgressbar(progressbar, "privateNets", true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
            $(this).dialog("close");
        }
    });

    $(document).on('click', '.delete-privateNet', function () {

        event.preventDefault();

        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        privateNet = document.getElementById(id + "-name-text");

        $('div#private-network-delete-confirm-form > p > span.privateNet-name').empty().append($(privateNet).text());

        $('#private-network-delete-confirm-form').dialog("open");
    });
});




