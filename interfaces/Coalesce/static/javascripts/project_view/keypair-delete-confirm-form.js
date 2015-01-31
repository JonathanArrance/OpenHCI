$(function () {

    var csrftoken = getCookie('csrftoken');
    var id = '';
    var keypair = '';
    var targetRow;

    // Widget Elements
    var progressbar = $("#keypair_progressbar"),
        placeholder =
            '<tr id="#keypair_placeholder"><td><p><i>You have no keys defined</i></p></td><td></td><td></td></tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#keypair-delete-confirm-form').dialog({
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
                    confKeypair = $(keypair).text();

                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                message.showMessage('notice', "Deleting " + confKeypair + ".");

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

                $.getJSON('/key_pair/' + confKeypair + '/' + PROJECT_ID + '/delete/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);
                            console.log(data);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();

                            // Update selects
                            removeFromSelect(confKeypair, $("#sec_key_name"), secKeyInstOpts)
                        }

                        // If last keypair, reveal placeholder
                        var rowCount = $('#keypair_list tr').length;
                        if (rowCount < 2) {
                            $('#keypair_list').append(placeholder).fadeIn();
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
        }
    });

    $(document).on('click', '.delete-keypair', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        keypair = document.getElementById(id + "-name-text");

        $('div#keypair-delete-confirm-form > p > span.keypair-name').empty().append($(keypair).text());

        $('#keypair-delete-confirm-form').dialog("open");
    });
});



