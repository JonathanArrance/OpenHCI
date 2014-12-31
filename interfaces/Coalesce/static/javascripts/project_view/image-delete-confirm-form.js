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
        image,
        targetRow;

    // Widget Elements
    var progressbar = $("#image_progressbar"),
        table = $("#image_list"),
        placeholder =
            '<tr id="#image_placeholder"><td><p><i>This project has no image</i></p></td><td></td></tr>';

    $('#image-delete-confirm-form').dialog({
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
                var confId = id,
                    confImage = $(image).text();

                message.showMessage('notice', "Deleting " + confImage + ".");

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and delete actions
                disableLinks(true);
                disableActions("delete-image", true);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "images", false);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/delete_image/' + confId + '/')
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
                            $(targetRow).fadeOut().remove();
                        }

                        // If last image, reveal placeholder
                        var rowCount = $('#image_list tr').length;
                        if (rowCount < 2) {
                            $(table).append(placeholder).fadeIn();
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
                        disableProgressbar(progressbar, "images", true);
                        disableLinks(false);
                        disableActions("delete-image", false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.delete-image', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the image-name-text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        image = document.getElementById(id + "-name-text");

        // Add image-name-text to confirm-form
        $('div#image-delete-confirm-form > p > span.image-name').empty().append($(image).text());

        $('#image-delete-confirm-form').dialog("open");
    });
});




