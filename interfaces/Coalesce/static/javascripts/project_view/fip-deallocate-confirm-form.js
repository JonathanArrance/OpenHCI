$(function () {

    var csrftoken = getCookie('csrftoken');
    var fip = '';
    var targetRow;
    var placeholder = '<tr id="fip_placeholder"><td><p><i>This project has no floating IPs</i></p></td><td></td><td></td></tr>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#fip-deallocate-confirm-form').dialog({
        autoOpen: false,
        height: 150,
        width: 350,
        modal: true,
        buttons: {
            "Confirm": function () {

                var confirmedFip = fip;
                var deallocateHtml = '<a id="' + confirmedFip + '" class="deallocate_ip" href="#">deallocate</a></td>';

                message.showMessage('notice', "Deallocating " + confirmedFip + ".");

                setVisible('.allocate_ip', false);
                setVisible('#assign_ip', false);
                disableLinks(true);

                // Create loader
                var actionsCell = document.getElementById(confirmedFip + "-actions-cell");
                var loaderId = confirmedFip + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/deallocate_floating_ip/' + PROJECT_ID + '/' + confirmedFip + '/')
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(deallocateHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();

                            var targetOption = 'select#assign_floating_ip option[value="' + confirmedFip + '"]';
                            $(targetOption).remove();
                        }

                        setVisible('.allocate_ip', true);

                        // If last fip, reveal placeholder and hide assign_ip
                        var rowCount = $('#fip_list tr').length;
                        if (rowCount < 2) {
                            $('#fip_list').append(placeholder).fadeIn();
                        } else {
                            setVisible('#assign_ip', true);
                        }

                        disableLinks(false);

                    })
                    .error(function () {
                        message.showMessage('error', 'Server Fault');

                        setVisible('.allocate_ip', true);
                        setVisible('#assign_ip', true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            },

            Cancel: function () {
                $(this).dialog("close");
            }
        }
    });

    $(document).on('click', '.deallocate_ip', function () {

        targetRow = $(this).parent().parent();
        fip = $(this).attr("id");

        $('div#fip-deallocate-confirm-form > p > span.ip-address').empty().append(fip);

        $('#fip-deallocate-confirm-form').dialog("open");
    });

    $(document).ready(function () {
        if ($('#fip_placeholder').length) {
            setVisible('#assign_ip', false)
        }
    });
});




