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
        fip,
        targetRow;

    // Widget Elements
    var progressbar = $("#fip_progressbar"),
        table = $("#fip_list"),
        placeholder =
            '<tr id="fip_placeholder"><td><p><i>This project has no floating IPs</i></p></td><td></td><td></td></tr>';

    $('#fip-deallocate-confirm-form').dialog({
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
                var confFip = fip,
                    confId = id;

                // Store actions cell html
                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = '<a class="deallocate_ip" href="#">deallocate</a></td>';

                message.showMessage('notice', "Deallocating " + confFip + ".");

                // Disable widget view links and hide allocate and assign buttons
                disableLinks(true);
                setVisible('#allocate_ip', false);
                setVisible('#assign_ip', false);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/deallocate_floating_ip/' + PROJECT_ID + '/' + confFip + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();

                            var targetOption = 'select#assign_floating_ip option[value="' + confId + '"]';
                            $(targetOption).remove();
                        }

                        // If last fip, reveal placeholder and hide assign_ip
                        var rowCount = $('#fip_list tr').length;
                        if (rowCount < 2) {
                            $(table).append(placeholder).fadeIn();
                        } else {
                            setVisible('#assign_ip', true);
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');
                    })
                    .always(function () {

                        setVisible(progressbar, false);
                        setVisible('#allocate_ip', true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function(){
        }
    });

    $(document).on('click', '.deallocate_ip', function () {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get form text
        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        fip = $(document.getElementById(id + "-ip-address")).text();

        $('div#fip-deallocate-confirm-form > p > span.ip-address').empty().append(fip);
        $('#fip-deallocate-confirm-form').dialog("open");
    });

    $(document).ready(function () {
        if ($('#fip_placeholder').length) {
            setVisible('#assign_ip', false)
        }
    });
});




