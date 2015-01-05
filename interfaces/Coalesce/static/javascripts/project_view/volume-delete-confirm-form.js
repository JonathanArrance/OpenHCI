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
    var progressbar = $("#vol_progressbar"),
        table = $("#volume_list"),
        placeholder =
            '<tr id="volume_placeholder"><td><p><i>This project has no volumes</i></p></td><td></td><td></td>/tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $("#volume-delete-confirm-form").dialog({
        autoOpen: false,
        height: 125,
        width: 235,
        modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position:{
            my: "center",
            at: "center",
            of: $('#page-content')
        },
        buttons: {
            "Confirm": function () {

                // Confirmed Selections
                var confRow = targetRow,
                    confId = id,
                    confVol = $(volume).text();

                message.showMessage('notice', "Deleting " + confVol + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and instance actions
                disableLinks(true);
                disableActions("delete-volume", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "volumes", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/delete_volume/' + confId + '/' + PROJECT_ID + '/')
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

                            // Remove volume
                            volumes.removeItem(confId);

                            // Update usedStorage
                            updateUsedStorage();
                            updateStorageBar();

                            // If last row, append placeholder
                            var rowCount = $('#volume_list tr').length;
                            if (rowCount < 2) {
                                $(table).append(placeholder).fadeIn();
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
                        disableProgressbar(progressbar, "volumes", true);
                        disableLinks(false);
                        disableActions("delete-volume", false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.delete-volume', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        volume = document.getElementById(id + "-name-text");

        // Add name-text to form
        $('div#volume-delete-confirm-form > p > span.volume-name').empty().append($(volume).text());

        $('#volume-delete-confirm-form').dialog("open");
    });
});
